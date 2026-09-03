"""!
@file viewers/media.py
@brief Media viewer widget for audio and video files.
"""

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QStyle
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

from viewers.base import BaseViewerWidget
from viewers.factory import ViewerFactory

@ViewerFactory.register([
    ".mp4", ".avi", ".mkv", ".mov",
    ".mp3", ".wav", ".flac", ".ogg"
])
class MediaViewerWidget(BaseViewerWidget):
    """!
    @brief Viewer widget for playing audio and video files.
    @details Utilizes PyQt6.QtMultimedia for media playback. Provides basic
             playback controls (Play, Pause, Stop) and a seek slider.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """!
        @brief Initialize media viewer widget.
        @param parent Optional parent widget.
        """
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # Media Player components
        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)

        # Video Display
        self._video_widget = QVideoWidget()
        self._player.setVideoOutput(self._video_widget)
        self._layout.addWidget(self._video_widget, stretch=1)

        # Controls UI
        self._controls_layout = QHBoxLayout()
        self._controls_layout.setContentsMargins(5, 5, 5, 5)
        self._controls_layout.setSpacing(5)

        # Buttons
        self._play_btn = QPushButton()
        self._play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self._play_btn.clicked.connect(self._toggle_playback)

        self._stop_btn = QPushButton()
        self._stop_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self._stop_btn.clicked.connect(self._player.stop)

        self._controls_layout.addWidget(self._play_btn)
        self._controls_layout.addWidget(self._stop_btn)

        # Slider
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(0, 0)
        self._slider.sliderMoved.connect(self._set_position)
        self._controls_layout.addWidget(self._slider)

        # Time Label
        self._time_label = QLabel("00:00 / 00:00")
        self._controls_layout.addWidget(self._time_label)

        self._layout.addLayout(self._controls_layout)

        # Connect signals
        self._player.positionChanged.connect(self._position_changed)
        self._player.durationChanged.connect(self._duration_changed)
        self._player.playbackStateChanged.connect(self._state_changed)
        self._player.hasVideoChanged.connect(self._video_changed)

    def _toggle_playback(self) -> None:
        """!
        @brief Toggle between play and pause states.
        """
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
        else:
            self._player.play()

    def _state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        """!
        @brief Update play/pause button icon based on playback state.
        @param state New playback state.
        """
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self._play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self._play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def _position_changed(self, position: int) -> None:
        """!
        @brief Update slider and time label when playback position changes.
        @param position New position in milliseconds.
        """
        self._slider.setValue(position)
        self._update_time_label(position, self._player.duration())

    def _duration_changed(self, duration: int) -> None:
        """!
        @brief Update slider range when media duration changes.
        @param duration New duration in milliseconds.
        """
        self._slider.setRange(0, duration)

    def _set_position(self, position: int) -> None:
        """!
        @brief Seek to a specific position in the media.
        @param position Target position in milliseconds.
        """
        self._player.setPosition(position)

    def _update_time_label(self, position: int, duration: int) -> None:
        """!
        @brief Format and update the time label.
        @param position Current position in milliseconds.
        @param duration Total duration in milliseconds.
        """
        def format_time(ms: int) -> str:
            s = ms // 1000
            m = s // 60
            s = s % 60
            return f"{m:02}:{s:02}"
        
        self._time_label.setText(f"{format_time(position)} / {format_time(duration)}")

    def _video_changed(self, has_video: bool) -> None:
        """!
        @brief Show or hide video widget depending on media type.
        @param has_video True if media contains video track.
        """
        if has_video:
            self._video_widget.show()
        else:
            self._video_widget.hide()

    def load_file(self, filepath: str) -> bool:
        """!
        @brief Load an audio or video file.
        @param filepath Path to the media file.
        @return True if successful.
        """
        self._current_filepath = filepath
        url = QUrl.fromLocalFile(filepath)
        self._player.setSource(url)
        # We start paused or stopped by default. 
        # The user has to click play.
        # Ensure video widget visibility is updated.
        self._video_widget.show()
        return True

    def clear(self) -> None:
        """!
        @brief Stop playback and release media.
        """
        super().clear()
        self._player.stop()
        self._player.setSource(QUrl())
