import os
import cv2
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import locale
import sys

try:
    import numpy as np
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    import numpy as np

try:
    import cv2
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python"])
    import cv2

class jp2convert_func:
    def __init__(self, root):
        self.root = root
        self.root.title("JP2 Convert")
        self.root.geometry("900x820")
        self.root.minsize(900, 820)
        
        # 시스템 로케일 설정 (파일 경로 인코딩 문제 해결용)(아스키코드가 아닌 한국어,중국어,일본어의 경우 경로오류 발생해서 넣음)
        if sys.platform.startswith('win'):
            locale.setlocale(locale.LC_ALL, '')
        
        # 언어 설정
        self.current_language = tk.StringVar(value="한국어")
        
        # 번역용 딕셔너리
        self.translations = {
            "한국어": {
                "title": "JP2 변환기",
                "file_select": "파일 선택",
                "jp2_folder": "jp2 폴더:",
                "output": "출력 폴더:",
                "browse_button": "파일 선택",
                "option": "옵션",
                "output_format": "출력 형식:",
                "png_format": "PNG (.png) - 무손실 압축",
                "jpg_format": "JPEG (.jpg) - 손실 압축, 작은 파일 크기",
                "tiff_format": "TIFF (.tiff) - 무손실 또는 손실 압축",
                "bmp_format": "BMP (.bmp) - 무압축, 큰 파일 크기",
                "webp_format": "WebP (.webp) - 웹용 이미지 형식",
                "jpeg_quality": "JPEG 품질:",
                "png_compression": "PNG 압축:",
                "webp_quality": "WebP 품질:",
                "low_high": "(낮음 ← → 높음)",
                "convert_button": "변환 시작",
                "cancel_button": "취소",
                "progress_frame": "진행 상황",
                "current_file": "현재 파일:",
                "progress": "진척도:",
                "waiting": "기다리는 중...",
                "log_frame": "변환 로그",
                "error_input": "오류: 입력 폴더를 선택해주세요.",
                "error_output": "오류: 출력 폴더를 선택해주세요.",
                "no_jp2": "정보: 입력 폴더에 JP2 파일이 없습니다.",
                "converting": "변환 중... ({}/{})",
                "quality_info": ", 품질: {}%",
                "compression_info": ", 압축: {}",
                "start_conversion": "변환 시작: {}개의 JP2 파일을 {} 형식으로 변환합니다{}.",
                "error_read": "오류: {} 파일을 읽을 수 없습니다.",
                "error_encode": "오류: {} 파일을 인코딩할 수 없습니다.",
                "error_convert": "파일 변환 중 오류 발생: {}\n오류 메시지: {}",
                "convert_log": "변환: {} -> {}",
                "completed": "변환 완료: {}개의 파일이 변환되었습니다.",
                "complete_message": "모든 파일 변환이 완료되었습니다.\n총 {}개의 파일이 변환되었습니다.",
                "cancelled": "변환이 사용자에 의해 취소되었습니다.",
                "confirm_cancel": "변환을 취소하시겠습니까?",
                "browse_input": "JP2 파일이 있는 폴더 선택",
                "browse_output": "변환된 이미지를 저장할 폴더 선택",
            },
            "English": {
                "title": "JP2 Converter",
                "file_select": "File Selection",
                "jp2_folder": "JP2 Folder:",
                "output": "Output Folder:",
                "browse_button": "Browse",
                "option": "Options",
                "output_format": "Output Format:",
                "png_format": "PNG (.png) - Lossless compression",
                "jpg_format": "JPEG (.jpg) - Lossy compression, small file size",
                "tiff_format": "TIFF (.tiff) - Lossless or lossy compression",
                "bmp_format": "BMP (.bmp) - No compression, large file size",
                "webp_format": "WebP (.webp) - Web image format",
                "jpeg_quality": "JPEG Quality:",
                "png_compression": "PNG Compression:",
                "webp_quality": "WebP Quality:",
                "low_high": "(LOW ← → HIGH)",
                "convert_button": "Start Conversion",
                "cancel_button": "Cancel",
                "progress_frame": "Progress",
                "current_file": "Current File:",
                "progress": "Progress:",
                "waiting": "Waiting...",
                "log_frame": "Conversion Log",
                "error_input": "Error: Please select an input folder.",
                "error_output": "Error: Please select an output folder.",
                "no_jp2": "Info: No JP2 files in the input folder.",
                "converting": "Converting... ({}/{})",
                "quality_info": ", Quality: {}%",
                "compression_info": ", Compression: {}",
                "start_conversion": "Starting conversion: {} JP2 files will be converted to {} format{}.",
                "error_read": "Error: Cannot read file {}.",
                "error_encode": "Error: Cannot encode file {}.",
                "error_convert": "Error during file conversion: {}\nError message: {}",
                "convert_log": "Converting: {} -> {}",
                "completed": "Conversion complete: {} files converted.",
                "complete_message": "All file conversions completed.\nTotal files converted: {}.",
                "cancelled": "Conversion was cancelled by user.",
                "confirm_cancel": "Do you want to cancel the conversion?",
                "browse_input": "Select folder with JP2 files",
                "browse_output": "Select folder to save converted images",
            }
        }
        
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.output_format = tk.StringVar(value="")

        # 실제 값을 저장할 변수들
        self.quality_value = tk.DoubleVar(value=75.0)
        self.compression_value = tk.DoubleVar(value=6.0)
        self.webp_quality_value = tk.DoubleVar(value=75.0)
        
        # 표시용 변수들 (소수점 1자리까지 표시)
        self.quality_display_value = tk.StringVar(value="75.0")
        self.compression_display_value = tk.StringVar(value="6.0")
        self.webp_quality_display_value = tk.StringVar(value="75.0")
        
        self.processing = False
        self.current_file = tk.StringVar(value="")
        self.progress_value = tk.DoubleVar(value=0.0)
        self.file_count = tk.IntVar(value=0)
        self.processed_count = tk.IntVar(value=0)
        self.preview_image = None

        self.format_quality_settings = {
            "jpg": 90,  # JPEG 품질 (0-100)
            "png": 6,   # PNG 압축 수준 (0-9)
            "webp": 90  # WebP 품질 (0-100)
        }
        
        # 초기 출력 형식 설정
        self.formats = []
        self.update_format_list()
        
        # UI 생성
        self.create_ui()
        
        # 드롭다운 목록(콤보박스) - on_format_changed으로 숨길 수 있게
        self.format_combo.bind("<<ComboboxSelected>>", self.on_format_changed)
    
    def get_text(self, key):
        #현재 언어에 맞는 텍스트를 반환
        lang = self.current_language.get()
        return self.translations[lang].get(key, key)
    
    def update_format_list(self):
        #현재 언어에 맞게 이미지 출력 목록 업데이트
        lang = self.current_language.get()
        self.formats = [
            self.translations[lang]["png_format"],
            self.translations[lang]["jpg_format"],
            self.translations[lang]["tiff_format"],
            self.translations[lang]["bmp_format"],
            self.translations[lang]["webp_format"]
        ]
        
        # 처음 실행 시 이미지 출력 설정
        if not self.output_format.get():
            self.output_format.set(self.formats[0])
    
    def update_language(self):
        """        언어 변경 시 UI 텍스트 업데이트        """
        # 창 제목 업데이트
        self.root.title(self.get_text("title"))
        
        # 폴더 선택 프레임 업데이트
        self.folder_select_frame.config(text=self.get_text("file_select"))
        self.input_label.config(text=self.get_text("jp2_folder"))
        self.input_button.config(text=self.get_text("browse_button"))
        self.output_label.config(text=self.get_text("output"))
        self.output_button.config(text=self.get_text("browse_button"))
        
        # 옵션 프레임 업데이트
        self.settings_frame.config(text=self.get_text("option"))
        self.format_label.config(text=self.get_text("output_format"))
        
        # 품질 설정 업데이트
        self.jpeg_quality_label.config(text=self.get_text("jpeg_quality"))
        self.jpeg_quality_range.config(text=self.get_text("low_high"))
        self.png_compression_label.config(text=self.get_text("png_compression"))
        self.png_compression_range.config(text=self.get_text("low_high"))
        self.webp_quality_label.config(text=self.get_text("webp_quality"))
        self.webp_quality_range.config(text=self.get_text("low_high"))
        
        # 버튼 업데이트
        self.convert_button.config(text=self.get_text("convert_button"))
        self.cancel_button.config(text=self.get_text("cancel_button"))
        
        # 진행 상황 프레임 업데이트
        self.progress_frame.config(text=self.get_text("progress_frame"))
        self.current_file_label.config(text=self.get_text("current_file"))
        self.progress_label.config(text=self.get_text("progress"))
        self.status_label.config(text=self.get_text("waiting"))
        
        # 로그 프레임 업데이트
        self.log_frame.config(text=self.get_text("log_frame"))
        
        # 출력 형식 콤보박스 업데이트
        self.update_format_list()
        current_format = self.output_format.get()
        self.format_combo['values'] = self.formats
        
        # 같은 인덱스의 형식 선택 유지
        if current_format:
            for lang in self.translations:
                for i, fmt in enumerate(self.formats):
                    if current_format in self.translations[lang].values():
                        self.output_format.set(self.formats[i])
                        break
    
    def create_ui(self):
        # 메인프레임
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 언어 선택 프레임
        language_frame = ttk.Frame(main_frame)
        language_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(language_frame, text="Language/언어:").pack(side=tk.LEFT, padx=5)
        language_combo = ttk.Combobox(language_frame, textvariable=self.current_language, values=["한국어", "English"], state="readonly", width=10)
        language_combo.pack(side=tk.LEFT, padx=5)
        language_combo.bind("<<ComboboxSelected>>", lambda e: self.update_language())
        
        # 폴더 선택 프레임
        self.folder_select_frame = ttk.LabelFrame(main_frame, text=self.get_text("file_select"), padding="25")
        self.folder_select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 입력파일
        self.input_label = ttk.Label(self.folder_select_frame, text=self.get_text("jp2_folder"))
        self.input_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(self.folder_select_frame, textvariable=self.input_folder, width=50).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.input_button = ttk.Button(self.folder_select_frame, text=self.get_text("browse_button"), command=self.browse_input_folder)
        self.input_button.grid(row=0, column=2, padx=5, pady=5)
        
        # 출력파일
        self.output_label = ttk.Label(self.folder_select_frame, text=self.get_text("output"))
        self.output_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(self.folder_select_frame, textvariable=self.output_folder, width=50).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.output_button = ttk.Button(self.folder_select_frame, text=self.get_text("browse_button"), command=self.browse_output_folder)
        self.output_button.grid(row=1, column=2, padx=5, pady=5)
        
        self.folder_select_frame.columnconfigure(1, weight=1)
        
        # 옵션
        self.settings_frame = ttk.LabelFrame(main_frame, text=self.get_text("option"), padding="25")
        self.settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 출력 형식
        self.format_label = ttk.Label(self.settings_frame, text=self.get_text("output_format"))
        self.format_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.format_combo = ttk.Combobox(self.settings_frame, textvariable=self.output_format, state="readonly", width=50)
        self.format_combo['values'] = self.formats
        self.format_combo.current(0)
        self.format_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 품질 설정 tk
        quality_frame = ttk.Frame(self.settings_frame)
        quality_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        # JPEG 품질
        self.jpeg_quality_frame = ttk.Frame(quality_frame)
        self.jpeg_quality_label = ttk.Label(self.jpeg_quality_frame, text=self.get_text("jpeg_quality"))
        self.jpeg_quality_label.pack(side=tk.LEFT, padx=5)
        self.jpeg_quality_scale = ttk.Scale(
            self.jpeg_quality_frame, 
            from_=0, 
            to=100, 
            variable=self.quality_value, 
            orient=tk.HORIZONTAL, 
            length=200,
            command=self.format_quality_value
        )
        self.jpeg_quality_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Label(self.jpeg_quality_frame, textvariable=self.quality_display_value).pack(side=tk.LEFT, padx=5)
        self.jpeg_quality_range = ttk.Label(self.jpeg_quality_frame, text=self.get_text("low_high"))
        self.jpeg_quality_range.pack(side=tk.LEFT)

        # PNG 압축
        self.png_compression_frame = ttk.Frame(quality_frame)
        self.png_compression_label = ttk.Label(self.png_compression_frame, text=self.get_text("png_compression"))
        self.png_compression_label.pack(side=tk.LEFT, padx=5)
        self.png_compression_scale = ttk.Scale(
            self.png_compression_frame, 
            from_=0, 
            to=9, 
            variable=self.compression_value, 
            orient=tk.HORIZONTAL, 
            length=200,
            command=self.format_compression_value
        )
        self.png_compression_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Label(self.png_compression_frame, textvariable=self.compression_display_value).pack(side=tk.LEFT, padx=5)
        self.png_compression_range = ttk.Label(self.png_compression_frame, text=self.get_text("low_high"))
        self.png_compression_range.pack(side=tk.LEFT)

        # WebP 품질
        self.webp_quality_frame = ttk.Frame(quality_frame)
        self.webp_quality_label = ttk.Label(self.webp_quality_frame, text=self.get_text("webp_quality"))
        self.webp_quality_label.pack(side=tk.LEFT, padx=5)
        self.webp_quality_scale = ttk.Scale(
            self.webp_quality_frame, 
            from_=0, 
            to=100, 
            variable=self.webp_quality_value,
            orient=tk.HORIZONTAL, 
            length=200,
            command=self.format_webp_quality_value
        )
        self.webp_quality_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Label(self.webp_quality_frame, textvariable=self.webp_quality_display_value).pack(side=tk.LEFT, padx=5)
        self.webp_quality_range = ttk.Label(self.webp_quality_frame, text=self.get_text("low_high"))
        self.webp_quality_range.pack(side=tk.LEFT)
        
        # 처음에는 PNG가 선택되므로 PNG 압축 설정만 표시
        self.jpeg_quality_frame.pack_forget()
        self.png_compression_frame.pack(fill=tk.X)
        self.webp_quality_frame.pack_forget()
        
        # 변환 버튼 및 진행 영역
        control_frame = ttk.Frame(main_frame, padding="10")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.convert_button = ttk.Button(control_frame, text=self.get_text("convert_button"), command=self.start_conversion)
        self.convert_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(control_frame, text=self.get_text("cancel_button"), command=self.cancel_conversion, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        # 진행 상황 표시용
        self.progress_frame = ttk.LabelFrame(main_frame, text=self.get_text("progress_frame"), padding="10")
        self.progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.current_file_label = ttk.Label(self.progress_frame, text=self.get_text("current_file"))
        self.current_file_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(self.progress_frame, textvariable=self.current_file).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.progress_label = ttk.Label(self.progress_frame, text=self.get_text("progress"))
        self.progress_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_value, maximum=100)
        self.progress_bar.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        self.status_label = ttk.Label(self.progress_frame, text=self.get_text("waiting"))
        self.status_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        self.progress_frame.columnconfigure(1, weight=1)
        
        # 로그 영역
        self.log_frame = ttk.LabelFrame(main_frame, text=self.get_text("log_frame"), padding="10")
        self.log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(self.log_frame, height=10, width=50, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        self.log_text.config(state=tk.DISABLED)

    def format_quality_value(self, event=None):
        """JPEG 품질 값을 소수점 1자리로 포맷팅"""
        value = self.quality_value.get()
        formatted_value = f"{value:.1f}"
        self.quality_display_value.set(formatted_value)

    def format_compression_value(self, event=None):
        """PNG 압축 값을 소수점 1자리로 포맷팅"""
        value = self.compression_value.get()
        formatted_value = f"{value:.1f}"
        self.compression_display_value.set(formatted_value)

    def format_webp_quality_value(self, event=None):
        """WebP 품질 값을 소수점 1자리로 포맷팅"""
        value = self.webp_quality_value.get()
        formatted_value = f"{value:.1f}"
        self.webp_quality_display_value.set(formatted_value)

    def on_format_changed(self, event):
        selected_format = self.output_format.get()
        
        # 숨기기
        self.jpeg_quality_frame.pack_forget()
        self.png_compression_frame.pack_forget()
        self.webp_quality_frame.pack_forget()
        
        # 어떤 품질 선택했는지에 따라서 해당 설정 표시
        if self.get_text("jpg_format") in selected_format:
            self.jpeg_quality_frame.pack(fill=tk.X)
            self.quality_value.set(self.format_quality_settings["jpg"])
        elif self.get_text("png_format") in selected_format:
            self.png_compression_frame.pack(fill=tk.X)
            self.compression_value.set(self.format_quality_settings["png"])
        elif self.get_text("webp_format") in selected_format:
            self.webp_quality_frame.pack(fill=tk.X)
            self.quality_value.set(self.format_quality_settings["webp"])
    
    def browse_input_folder(self):
        folder = filedialog.askdirectory(title=self.get_text("browse_input"))
        if folder:
            self.input_folder.set(folder)
            if not self.output_folder.get():
                self.output_folder.set(os.path.join(folder, "converted"))
    
    def browse_output_folder(self):
        folder = filedialog.askdirectory(title=self.get_text("browse_output"))
        if folder:
            self.output_folder.set(folder)
    
    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def start_conversion(self):
        if not self.input_folder.get():
            messagebox.showerror("Error", self.get_text("error_input"))
            return
        
        if not self.output_folder.get():
            messagebox.showerror("Error", self.get_text("error_output"))
            return
        
        # 출력 폴더가 없으면 생성
        if not os.path.exists(self.output_folder.get()):
            os.makedirs(self.output_folder.get())
        
        # 출력 형식 설정
        format_mapping = {
            self.get_text("png_format"): "png",
            self.get_text("jpg_format"): "jpg",
            self.get_text("tiff_format"): "tiff",
            self.get_text("bmp_format"): "bmp",
            self.get_text("webp_format"): "webp"
        }
        
        selected_format = format_mapping.get(self.output_format.get(), "png")
        
        # 품질 설정 저장
        if selected_format == "jpg" or selected_format == "webp":
            self.format_quality_settings[selected_format] = self.quality_value.get()
        elif selected_format == "png":
            self.format_quality_settings[selected_format] = self.compression_value.get()
        
        # 모든 JP2 파일 찾기 - 미리 파일 수 확인
        jp2_files = []
        for root, dirs, files in os.walk(self.input_folder.get()):
            for file in files:
                if file.lower().endswith('.jp2'):
                    jp2_files.append(os.path.join(root, file))
        
        if not jp2_files:
            messagebox.showinfo("Info", self.get_text("no_jp2"))
            return
        
        self.file_count.set(len(jp2_files))
        self.processed_count.set(0)
        self.progress_value.set(0)
        
        # UI 상태 업데이트
        self.convert_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.status_label.config(text=self.get_text("converting").format(0, self.file_count.get()))
        self.processing = True
        
        # 로그 초기화
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # 품질 설정 로깅
        quality_info = ""
        if selected_format == "jpg":
            quality_info = self.get_text("quality_info").format(int(self.format_quality_settings['jpg']))
        elif selected_format == "png":
            quality_info = self.get_text("compression_info").format(int(self.format_quality_settings['png']))
        elif selected_format == "webp":
            quality_info = self.get_text("quality_info").format(int(self.format_quality_settings['webp']))
        
        self.log(self.get_text("start_conversion").format(len(jp2_files), selected_format.upper(), quality_info))
        
        # 변환 작업 시작 (별도 스레드)
        threading.Thread(target=self.convert_files, args=(jp2_files, selected_format), daemon=True).start()
    
    def convert_files(self, jp2_files, output_format):
        for idx, input_path in enumerate(jp2_files):
            if not self.processing:
                break
            
            try:
                # 상대 경로 계산 (UTF-8 인코딩 처리)
                input_path_normalized = os.path.normpath(input_path)
                input_folder_normalized = os.path.normpath(self.input_folder.get())
                
                # rel_path에 상대경로 저장(정규화)
                rel_path = os.path.relpath(input_path_normalized, input_folder_normalized)
                self.current_file.set(rel_path)
                
                # 파일 변환 작업(핵심)
                output_filename = os.path.splitext(os.path.basename(input_path_normalized))[0] + f".{output_format}"
                
                # 상대 경로 유지를 위한 디렉토리 구조 생성
                rel_dir = os.path.dirname(rel_path)
                output_dir = os.path.join(self.output_folder.get(), rel_dir)
                
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                
                output_path = os.path.join(output_dir, output_filename)
                
                # 진행 상황 로그에 표시
                self.root.after(0, lambda idx=idx, total=len(jp2_files), in_path=input_path, out_path=output_path: 
                    self.update_progress(idx, total, in_path, out_path))
                
                # cv2.imdecode와 바이너리 모드 - 바이너리 모드 np.fromfile(input_path, dtype=np.uint8)로 읽어 cv2.imdecode를 통해 이미지로 변환
                img = cv2.imdecode(np.fromfile(input_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                
                if img is None:
                    self.root.after(0, lambda path=input_path: self.log(self.get_text("error_read").format(path)))
                    continue

                # 이미지 저장 - 형식별 품질 설정 적용
                if output_format == "jpg":
                    quality = int(self.format_quality_settings["jpg"])
                    success, buffer = cv2.imencode(f".{output_format}", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
                elif output_format == "png":
                    compression = int(self.format_quality_settings["png"])
                    success, buffer = cv2.imencode(f".{output_format}", img, [cv2.IMWRITE_PNG_COMPRESSION, compression])
                elif output_format == "webp":
                    quality = int(self.format_quality_settings["webp"])
                    success, buffer = cv2.imencode(f".{output_format}", img, [cv2.IMWRITE_WEBP_QUALITY, quality])
                else:
                    success, buffer = cv2.imencode(f".{output_format}", img)
                
                if success:
                    with open(output_path, "wb") as f:
                        f.write(buffer)
                else:
                    self.root.after(0, lambda path=input_path: self.log(self.get_text("error_encode").format(path)))
                
            except Exception as e:
                error_msg = self.get_text("error_convert").format(input_path=input_path, error=str(e))
                self.root.after(0, lambda msg=error_msg: self.log(msg))
        
        # 변환 완료 후 UI 업데이트
        self.root.after(0, self.conversion_completed)
    
    def update_progress(self, current_idx, total_files, input_path, output_path):
        self.processed_count.set(current_idx + 1)
        progress_percent = ((current_idx + 1) / total_files) * 100
        self.progress_value.set(progress_percent)
        self.status_label.config(text=f"converting... ({current_idx + 1}/{total_files})")
        self.log(self.get_text("convert_log").format(input_path, output_path))
    
    def conversion_completed(self):
        if self.processing:
            self.log(self.get_text("completed").format(self.processed_count.get()))
            messagebox.showinfo("Completed", self.get_text("complete_message").format(self.processed_count.get()))
        else:
            self.log(self.get_text("cancelled"))
        
        # UI 상태 초기화
        self.processing = False
        self.convert_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.status_label.config(text=self.get_text("waiting"))
        self.current_file.set("")
    
    def cancel_conversion(self):
        if messagebox.askyesno(self.get_text("cancel_button"), self.get_text("confirm_cancel")):
            self.processing = False

if __name__ == "__main__":
    root = tk.Tk()
    app = jp2convert_func(root)
    root.mainloop()