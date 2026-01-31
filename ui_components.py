# -*- coding: utf-8 -*-
"""
UI Components Module for EchoLearn
Handles Streamlit UI components and user interface logic
"""

import streamlit as st
import time
import pandas as pd
from typing import Dict, List, Optional, Any
from scoring import ScoringAnalytics

class UIComponents:
    """Handles UI components and user interface logic"""
    
    @staticmethod
    def display_question_navigation(current_index: int, total_questions: int, qa_data: Dict) -> None:
        """Display question navigation and progress"""
        col1, col2, col3 = st.columns([1, 4, 1])
        
        with col1:
            # Previous button - only enabled if not on first question
            if st.button("⬅️ Previous", disabled=(current_index == 0)):
                st.session_state.qa_index = current_index - 1
                st.rerun()
                
        with col2:
            # Show current question position and progress
            answered_count = len(st.session_state.used_q_indices)
            st.markdown(f"**Question level: {qa_data.get('level', 'Unknown')}**")
            st.markdown(f"**Progress: {answered_count} of {total_questions} answered**")
            
        with col3:
            # Next button - only enabled if not on last question
            if st.button("Next ➡️", disabled=(current_index == total_questions - 1)):
                st.session_state.qa_index = current_index + 1
                st.rerun()
    
    @staticmethod
    def display_mode_toggles() -> Dict[str, bool]:
        """Display mode toggles and return current settings"""
        col_adaptive, col_sm, col_info = st.columns([1, 1, 2])
        
        with col_adaptive:
            adaptive_mode = st.checkbox(
                "🎯 Adaptive Mode", 
                value=st.session_state.get('adaptive_mode', True),
                help="Enable intelligent difficulty adjustment based on performance"
            )
            if adaptive_mode != st.session_state.get('adaptive_mode', True):
                st.session_state.adaptive_mode = adaptive_mode
                st.rerun()
        
        with col_sm:
            selective_mutism_mode = st.checkbox(
                "🎙️ Selective Mutism Training", 
                value=st.session_state.get('selective_mutism_mode', False),
                help="Enable speech training mode - provides gentle encouragement for verbal responses, supportive feedback, and confidence building"
            )
            if selective_mutism_mode != st.session_state.get('selective_mutism_mode', False):
                st.session_state.selective_mutism_mode = selective_mutism_mode
                # Reset confidence and success tracking when toggling mode
                if selective_mutism_mode:
                    st.session_state.confidence_level = 1
                    st.session_state.success_streak = 0
                    st.info("🎙️ Selective Mutism Training Mode enabled! Focus on gentle speech practice with supportive feedback.")
                st.rerun()
        
        with col_info:
            if adaptive_mode and not selective_mutism_mode:
                current_difficulty = st.session_state.get('current_difficulty', 10)
                consecutive_wrong = st.session_state.get('consecutive_wrong_same_level', 0)
                st.caption(f"Current adaptive difficulty: **{current_difficulty}/20** | Consecutive wrong: **{consecutive_wrong}**")
            elif selective_mutism_mode:
                confidence_level = st.session_state.get('confidence_level', 1)
                success_streak = st.session_state.get('success_streak', 0)
                confidence_stars = "⭐" * confidence_level
                st.caption(f"🎙️ Speech Training | Confidence Level: {confidence_stars} | Success Streak: **{success_streak}**")
        
        return {
            'adaptive_mode': adaptive_mode,
            'selective_mutism_mode': selective_mutism_mode
        }
    
    @staticmethod
    def display_question_info(qa_data: Dict, adaptive_mode: bool = False) -> None:
        """Display question information and current difficulty"""
        st.markdown(f"**Q:** {qa_data['question']}")
        
        # Show score if already answered
        if qa_data.get('score') is not None:
            st.success(f"Scored: {qa_data['score']}/10")
        
        # Show current adaptive difficulty if in adaptive mode
        if adaptive_mode:
            current_qa_difficulty = qa_data.get('difficulty', UIComponents._get_difficulty_from_level(qa_data.get('level', 'Basic')))
            current_difficulty = st.session_state.get('current_difficulty', 10)
            st.info(f"🎯 Current Target Difficulty: {current_difficulty} | This Question: {current_qa_difficulty}")
    
    @staticmethod
    def display_tts_button(qa_data: Dict) -> None:
        """Display text-to-speech button"""
        if st.button("🔊 Read Question Aloud"):
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(qa_data["question"])
                engine.runAndWait()
            except Exception as e:
                st.warning(f"TTS failed: {e}")
    
    @staticmethod
    def display_audio_recording_interface(qa_data: Dict, current_index: int, selective_mutism_mode: bool = False) -> Optional[str]:
        """Display audio recording interface and return transcribed text"""
        if selective_mutism_mode:
            return UIComponents._display_selective_mutism_audio_interface(qa_data, current_index)
        else:
            return UIComponents._display_standard_audio_interface(qa_data, current_index)
    
    @staticmethod
    def _display_selective_mutism_audio_interface(qa_data: Dict, current_index: int) -> Optional[str]:
        """Display selective mutism audio interface"""
        st.markdown("### 🎙️ **Speech Training Practice**")
        st.info("💪 This is your chance to practice speaking! Remember, every attempt makes you stronger.")
        
        # More encouraging interface for selective mutism training
        col1, col2 = st.columns([2, 1])
        with col1:
            record_seconds = st.slider("Choose comfortable recording time:", 3, 10, 5, 
                                     help="Start with shorter times if you feel more comfortable")
        with col2:
            confidence_level = st.session_state.get('confidence_level', 1)
            if confidence_level >= 3:
                st.success("🌟 You're building great confidence!")
            elif confidence_level >= 2:
                st.info("😊 You're making progress!")
            else:
                st.info("🌱 Every step counts!")
        
        if st.button("🎙️ **Practice Speaking** - You've Got This!", key="speech_training"):
            try:
                # Extra encouraging message for selective mutism training
                st.success("🌟 Wonderful! You're being so brave by practicing speaking!")
                st.info("🎙️ Recording now... Take your time and speak when you're ready!")
                
                import sounddevice as sd
                import scipy.io.wavfile as wav
                import speech_recognition as sr
                import tempfile
                import os
                
                fs = 44100
                audio = sd.rec(int(record_seconds * fs), samplerate=fs, channels=1, dtype='int16')
                sd.wait()
                
                # Use temporary file for better performance
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    temp_wav_path = tmp_file.name
                    wav.write(temp_wav_path, fs, audio)
                
                # Transcribe with encouraging messages
                with st.spinner("🔍 Understanding your speech... You're doing great!"):
                    recognizer = sr.Recognizer()
                    try:
                        with sr.AudioFile(temp_wav_path) as source:
                            # Optimize recognizer settings
                            recognizer.energy_threshold = 300
                            recognizer.dynamic_energy_threshold = True
                            audio_data = recognizer.record(source)
                            text = recognizer.recognize_google(audio_data)
                            
                            st.success("🎉 Amazing! I heard what you said! You spoke clearly!")
                            st.text_area("What you said (so proud of you!):", value=text, key=f"speech_training_text_{current_index}")
                            
                            return text
                            
                    except sr.UnknownValueError:
                        st.warning("🤗 No worries! Sometimes it's hard to understand, but you were so brave to try!")
                        return None
                    except sr.RequestError as e:
                        st.warning("🤗 Technology can be tricky! The important thing is you tried speaking!")
                        return None
                    finally:
                        # Clean up temporary file
                        try:
                            os.unlink(temp_wav_path)
                        except:
                            pass
                        
            except Exception as e:
                st.warning("🤗 No worries! Technology can be tricky sometimes. The important thing is that you tried to speak!")
                st.info("💡 **Tip**: You can still practice by using the text option below. Every form of participation counts!")
                return None
        
        return None
    
    @staticmethod
    def _display_standard_audio_interface(qa_data: Dict, current_index: int) -> Optional[str]:
        """Display standard audio recording interface"""
        record_seconds = st.slider("Select recording time (seconds):", 3, 15, 5)
        
        if st.button("🎙️ Record Your Answer"):
            try:
                st.info("Recording... Speak now!")
                
                import sounddevice as sd
                import scipy.io.wavfile as wav
                import speech_recognition as sr
                import tempfile
                import os
                
                fs = 44100
                audio = sd.rec(int(record_seconds * fs), samplerate=fs, channels=1, dtype='int16')
                sd.wait()
                
                # Use temporary file for better performance
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    temp_wav_path = tmp_file.name
                    wav.write(temp_wav_path, fs, audio)
                
                # Transcribe with better error handling
                recognizer = sr.Recognizer()
                try:
                    with st.spinner("🎙️ Processing your speech..."):
                        with sr.AudioFile(temp_wav_path) as source:
                            # Optimize recognizer settings for faster processing
                            recognizer.energy_threshold = 300
                            recognizer.dynamic_energy_threshold = True
                            audio_data = recognizer.record(source)
                            text = recognizer.recognize_google(audio_data)
                            
                            st.success("✅ Transcription Successful")
                            st.text_area("Your Answer (from audio)", value=text, key=f"audio_text_{current_index}")
                            
                            return text
                            
                except sr.UnknownValueError:
                    st.error("❌ Could not understand audio. Please try speaking more clearly.")
                    return None
                except sr.RequestError as e:
                    st.error(f"❌ Speech recognition service error: {e}")
                    return None
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(temp_wav_path)
                    except:
                        pass
                        
            except Exception as e:
                st.error(f"❌ Error during recording: {e}")
                st.info("💡 Make sure your microphone is working and you've granted permission.")
                return None
        
        return None
    
    @staticmethod
    def display_text_input(qa_data: Dict, current_index: int, selective_mutism_mode: bool = False) -> str:
        """Display text input interface"""
        if selective_mutism_mode:
            st.markdown("---")
            st.markdown("### ✍️ **Alternative: Write Your Answer**")
            st.info("🌱 If speaking feels too hard right now, you can write your answer. This is also great practice!")
            
            return st.text_area(
                "Type your answer here:", 
                value=qa_data.get("user_answer", ""), 
                key=f"backup_answer_{current_index}",
                help="Writing is also a wonderful way to express your thoughts!"
            )
        else:
            return st.text_area("Edit Your Answer", value=qa_data.get("user_answer", ""), key=f"user_answer_{current_index}")
    
    @staticmethod
    def display_submit_button(mode: str = "standard") -> bool:
        """Display submit button with appropriate text"""
        if mode == "selective_mutism_text":
            return st.button("📝 Submit Written Answer", key="backup_submit")
        else:
            return st.button("✅ Submit Answer")
    
    @staticmethod
    def display_evaluation_result(evaluation_result: Dict, mode: str = "standard") -> None:
        """Display evaluation result with appropriate messaging"""
        score = evaluation_result.get('score', 0)
        
        if mode == "selective_mutism":
            # Display encouraging messages for selective mutism
            encouragement = evaluation_result.get('encouragement', 'Great job!')
            feedback = evaluation_result.get('feedback', 'You\'re doing wonderfully!')
            
            st.success(f"✨ {encouragement}")
            st.info(f"💪 **{feedback}**")
            
            # Special celebration for good scores
            if score >= 6:
                st.balloons()
                st.success("🎙️ **You did it! You spoke up and that's incredible!** Your voice matters!")
            else:
                st.info("🎙️ **You were so brave to speak! Every time you practice, you get stronger!**")
        else:
            # Standard evaluation display
            st.success(f"✅ Answer saved and scored: {score}/10")
            
            # Show detailed feedback if available
            if 'feedback' in evaluation_result:
                st.info(f"💡 **Feedback:** {evaluation_result['feedback']}")
            if 'suggestions' in evaluation_result:
                st.info(f"📚 **Suggestions:** {evaluation_result['suggestions']}")
    
    @staticmethod
    def display_session_statistics(evaluations: List[Dict]) -> None:
        """Display session statistics"""
        if not evaluations:
            return
        
        st.subheader("📊 Session Statistics")
        
        stats = ScoringAnalytics.calculate_session_statistics(evaluations)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Questions", stats['total_questions'])
        col2.metric("Answered", stats['answered_questions'])
        col3.metric("Score", f"{stats['total_score']}/{stats['max_possible_score']}")
        if stats['answered_questions'] > 0:
            col4.metric("Average Score", f"{stats['average_score']:.1f}/10")
        else:
            col4.metric("Average Score", "0/10")
    
    @staticmethod
    def display_final_score_report(evaluations: List[Dict]) -> None:
        """Display comprehensive final score report"""
        st.subheader("🏆 Final Score Report")
        
        stats = ScoringAnalytics.calculate_session_statistics(evaluations)
        
        # Display main metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="🎯 Overall Score",
                value=f"{stats['total_score']}/{stats['max_possible_score']}",
                delta=f"{stats['percentage']:.1f}%"
            )
        
        with col2:
            st.metric(
                label="📊 Average per Question",
                value=f"{stats['average_score']:.1f}/10",
                delta=f"{(stats['average_score']/10)*100:.0f}%"
            )
        
        with col3:
            grade_messages = {
                "A+": "🏅 Outstanding!",
                "A": "⭐ Excellent!",
                "B": "😊 Good Job!",
                "C": "👍 Fair Performance",
                "D": "💪 Need Improvement",
                "F": "📚 Keep Studying!"
            }
            delta_message = grade_messages.get(stats['grade'], "No questions answered")
            st.metric(
                label="🏅 Final Grade",
                value=stats['grade'],
                delta=delta_message
            )
        
        # Difficulty distribution analysis
        if evaluations:
            UIComponents._display_difficulty_analysis(evaluations)
        
        # Selective Mutism Progress Insights (if applicable)
        if st.session_state.get('selective_mutism_mode', False):
            UIComponents._display_selective_mutism_progress()
        
        # Adaptive learning insights (if applicable)
        elif st.session_state.get('adaptive_mode', False):
            UIComponents._display_adaptive_learning_insights()
    
    @staticmethod
    def _display_difficulty_analysis(evaluations: List[Dict]) -> None:
        """Display difficulty distribution analysis"""
        st.subheader("📈 Performance by Difficulty")
        
        difficulty_stats = ScoringAnalytics.analyze_difficulty_performance(evaluations)
        
        for diff_range, stats in difficulty_stats.items():
            st.write(f"**{diff_range}:** {stats['count']} questions, {stats['average']:.1f}/10 avg ({stats['percentage']:.1f}%)")
            st.progress(stats['percentage'] / 100)
    
    @staticmethod
    def _display_selective_mutism_progress() -> None:
        """Display selective mutism progress insights"""
        st.subheader("🤝 Selective Mutism Progress")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            confidence_level = st.session_state.get('confidence_level', 1)
            confidence_stars = "⭐" * confidence_level
            st.metric(
                "Confidence Level",
                f"{confidence_stars} ({confidence_level}/5)",
                help="Your confidence has grown through successful participation"
            )
        
        with col2:
            success_streak = st.session_state.get('success_streak', 0)
            st.metric(
                "Success Streak",
                str(success_streak),
                help="Consecutive good answers (builds confidence)"
            )
        
        with col3:
            # Count milestones achieved
            milestones = st.session_state.get('sm_progress_milestones', [])
            milestones_achieved = len([m for m in milestones if m.get('type') == 'confidence_increase'])
            st.metric(
                "Confidence Milestones",
                str(milestones_achieved),
                help="Times you've leveled up in confidence"
            )
        
        # Encouragement based on progress
        confidence_level = st.session_state.get('confidence_level', 1)
        if confidence_level >= 4:
            st.success("🌟 Amazing! You've built tremendous confidence. You should be very proud of your progress!")
        elif confidence_level >= 3:
            st.success("🎉 Great job! Your confidence is growing strong. Keep up the excellent work!")
        elif confidence_level >= 2:
            st.info("😊 You're making good progress! Each question you answer builds your confidence.")
        else:
            st.info("🌱 You've taken the first step, and that's wonderful! Every answer helps you grow.")
    
    @staticmethod
    def _display_adaptive_learning_insights() -> None:
        """Display adaptive learning insights"""
        st.subheader("🧠 Adaptive Learning Insights")
        
        difficulty_path = st.session_state.get('difficulty_path', [])
        if not difficulty_path:
            return
        
        # Calculate learning trajectory
        initial_difficulty = difficulty_path[0]['difficulty']
        final_difficulty = st.session_state.get('current_difficulty', 10)
        difficulty_change = final_difficulty - initial_difficulty
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Starting Difficulty",
                f"{initial_difficulty}/20",
                help="Difficulty level of first question"
            )
        
        with col2:
            st.metric(
                "Final Difficulty", 
                f"{final_difficulty}/20",
                delta=f"{difficulty_change:+d}"
            )
        
        with col3:
            correct_answers = sum(1 for step in difficulty_path if step.get('correct', False))
            accuracy = (correct_answers / len(difficulty_path)) * 100 if difficulty_path else 0
            st.metric(
                "Accuracy Rate",
                f"{accuracy:.1f}%",
                delta=f"{correct_answers}/{len(difficulty_path)}"
            )
        
        # Learning trajectory chart
        if len(difficulty_path) > 1:
            st.write("**📈 Learning Trajectory:**")
            
            difficulty_progression = [step['difficulty'] for step in difficulty_path]
            scores_progression = [step['score'] for step in difficulty_path]
            
            df = pd.DataFrame({
                'Question': range(1, len(difficulty_progression) + 1),
                'Difficulty Level': difficulty_progression,
                'Score': scores_progression
            })
            
            st.line_chart(df.set_index('Question'))
            
            # Performance insights
            if difficulty_change > 0:
                st.success(f"🚀 Great progress! You advanced {difficulty_change} difficulty levels.")
            elif difficulty_change == 0:
                st.info("🎯 You maintained a consistent difficulty level throughout the session.")
            else:
                st.info(f"📚 The system adapted to your learning pace, focusing on foundational concepts.")
    
    @staticmethod
    def display_adaptive_progress() -> None:
        """Display adaptive learning progress visualization"""
        difficulty_path = st.session_state.get('difficulty_path', [])
        if not difficulty_path:
            return
        
        # Show recent difficulty changes
        recent_steps = difficulty_path[-5:] if len(difficulty_path) > 5 else difficulty_path
        
        st.write("**Recent Progress:**")
        for i, step in enumerate(recent_steps, 1):
            status = "✅" if step.get('correct', False) else "❌"
            st.write(f"{status} Q{step.get('question_index', 0)+1}: Difficulty {step['difficulty']} → Score {step['score']}/10")
        
        # Show difficulty trend
        if len(difficulty_path) >= 3:
            recent_difficulties = [step['difficulty'] for step in difficulty_path[-3:]]
            if recent_difficulties[-1] > recent_difficulties[0]:
                st.success("📈 Trending upward in difficulty!")
            elif recent_difficulties[-1] < recent_difficulties[0]:
                st.info("📉 Focusing on strengthening fundamentals")
            else:
                st.info("🎯 Maintaining consistent challenge level")
    
    @staticmethod
    def display_report_download(evaluations: List[Dict], user_info: Dict) -> None:
        """Display report download functionality"""
        st.subheader("📄 Download Q&A + Scores")
        
        if st.button("📥 Generate Report"):
            # Generate report content
            report_content = UIComponents._generate_report_content(evaluations, user_info)
            
            st.download_button(
                label="Download as Text File",
                data=report_content,
                file_name=f"viva_evaluation_report_{user_info.get('username', 'user')}_{int(time.time())}.txt",
                mime="text/plain"
            )
    
    @staticmethod
    def _generate_report_content(evaluations: List[Dict], user_info: Dict) -> str:
        """Generate report content"""
        import io
        
        output = io.StringIO()
        output.write(f"Name: {user_info.get('full_name', user_info.get('username', 'N/A'))}\n")
        output.write(f"Subject: {user_info.get('subject', 'N/A')}\n")
        output.write(f"Book Title: {user_info.get('book_title', 'N/A')}\n\n")
        output.write("Structured Viva Questions, Answers, and Scores\n")
        output.write("=" * 70 + "\n\n")
        
        for i, eval_data in enumerate(evaluations, 1):
            output.write(f"[{i}] Difficulty: {eval_data.get('level', 'Unknown')}\n")
            output.write(f"Q: {eval_data.get('question', 'N/A')}\n")
            output.write(f"LLM Answer: {eval_data.get('answer', 'N/A')}\n")
            output.write(f"User Answer: {eval_data.get('user_answer', '[Not answered]')}\n")
            output.write(f"Score: {eval_data.get('score', '[Not evaluated]')} / 10\n")
            output.write("-" * 70 + "\n")
        
        return output.getvalue()
    
    @staticmethod
    def _get_difficulty_from_level(level: str) -> int:
        """Convert text levels to numeric difficulty for compatibility"""
        mapping = {
            'Basic': 3, 'Easy': 3,
            'Intermediate': 8, 'Moderate': 8, 
            'Advanced': 13, 'Difficult': 13,
            'Expert': 18
        }
        return mapping.get(level, 10)
