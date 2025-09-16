from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReadingSessionForm
from apps.students.models import Student
import subprocess
from django.contrib import messages
from .models import ReadingSession
import requests
import os
import json

def reading_session_create(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == 'POST':
        form = ReadingSessionForm(request.POST, request.FILES)
        if form.is_valid():
            session = form.save(commit=False)
            session.student = student
            session.save()
            return redirect('student_reading_sessions', student_id=student.id)
    else:
        form = ReadingSessionForm(initial={'student': student})
    return render(request, 'reading_sessions/reading_session_form.html', {'form': form, 'student': student})

def student_reading_sessions(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    sessions = student.reading_sessions.all()
    return render(request, 'reading_sessions/reading_session_list.html', {'student': student, 'sessions': sessions})

def generate_transcript(request, session_id):
    session = get_object_or_404(ReadingSession, pk=session_id)
    audio_path = session.audio.path
    try:
        with open(audio_path, "rb") as f:
            response = requests.post(
                "http://192.168.137.72:9000/transcribe/",
                files={"file": (os.path.basename(session.audio.name), f, "audio/mpeg")}
            )
        if response.status_code == 200:
            transcript = response.json()["result"]
            json_path = audio_path.replace(".mp3", ".json")
            with open(json_path, "w", encoding="utf-8") as out_f:
                json.dump(transcript, out_f, ensure_ascii=False, indent=2)
            messages.success(request, "Transcript generated and saved!")
        else:
            messages.error(request, f"Error: {response.text}")
    except Exception as e:
        messages.error(request, f"Error generating transcript: {e}")
    return redirect('reading_session_detail', session_id=session.id)

def reading_session_detail(request, session_id):
    session = get_object_or_404(ReadingSession, pk=session_id)
    transcript = None
    if session.audio:
        json_path = session.audio.path.replace('.mp3', '.json')
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                transcript = json.load(f)
    return render(request, 'reading_sessions/reading_session_detail.html', {
        'session': session,
        'transcript': transcript,
    })
