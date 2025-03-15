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
        
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.output_format = tk.StringVar(value="PNG (.png) - 무손실 압축")

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
        
        #UI
        self.create_ui()
        
        # 드롭다운 목록(콤보박스) - on_format_changed으로 숨길 수 있게
        self.format_combo.bind("<<ComboboxSelected>>", self.on_format_changed)
    
    def create_ui(self):
        # 메인프레임
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 폴더 선택 프레임
        folder_select_frame = ttk.LabelFrame(main_frame, text="파일 선택", padding="25")
        folder_select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 입력파일
        ttk.Label(folder_select_frame, text="jp2 폴더:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(folder_select_frame, textvariable=self.input_folder, width=50).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(folder_select_frame, text="파일 선택", command=self.browse_input_folder).grid(row=0, column=2, padx=5, pady=5)
        
        # 출력파일
        ttk.Label(folder_select_frame, text="Output:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(folder_select_frame, textvariable=self.output_folder, width=50).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(folder_select_frame, text="파일 선택", command=self.browse_output_folder).grid(row=1, column=2, padx=5, pady=5)
        
        folder_select_frame.columnconfigure(1, weight=1)
        
        # 옵션
        settings_frame = ttk.LabelFrame(main_frame, text="Option", padding="25")
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 출력 형식
        ttk.Label(settings_frame, text="출력 형식:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.formats = [
            "PNG (.png) - 무손실 압축",
            "JPEG (.jpg) - 손실 압축, 작은 파일 크기",
            "TIFF (.tiff) - 무손실 또는 손실 압축",
            "BMP (.bmp) - 무압축, 큰 파일 크기",
            "WebP (.webp) - 웹용 이미지 형식"
        ]
        
        self.format_combo = ttk.Combobox(settings_frame, textvariable=self.output_format, state="readonly", width=50)
        self.format_combo['values'] = self.formats
        self.format_combo.current(0)
        self.format_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 품질 설정 tk
        quality_frame = ttk.Frame(settings_frame)
        quality_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        # JPEG 품질
        self.jpeg_quality_frame = ttk.Frame(quality_frame)
        ttk.Label(self.jpeg_quality_frame, text="JPEG Quality:").pack(side=tk.LEFT, padx=5)
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
        ttk.Label(self.jpeg_quality_frame, textvariable=self.quality_display_value).pack(side=tk.LEFT, padx=5)  # 표시용 변수 사용
        ttk.Label(self.jpeg_quality_frame, text="(LOW ← → HIGH)").pack(side=tk.LEFT)

        # PNG 압축
        self.png_compression_frame = ttk.Frame(quality_frame)
        ttk.Label(self.png_compression_frame, text="PNG Compression:").pack(side=tk.LEFT, padx=5)
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
        ttk.Label(self.png_compression_frame, textvariable=self.compression_display_value).pack(side=tk.LEFT, padx=5)  # 표시용 변수 사용
        ttk.Label(self.png_compression_frame, text="(LOW ← → HIGH)").pack(side=tk.LEFT)

        # WebP 품질
        self.webp_quality_frame = ttk.Frame(quality_frame)
        ttk.Label(self.webp_quality_frame, text="WebP Quality:").pack(side=tk.LEFT, padx=5)
        self.webp_quality_scale = ttk.Scale(
            self.webp_quality_frame, 
            from_=0, 
            to=100, 
            variable=self.webp_quality_value,  # WebP용 별도 변수 사용
            orient=tk.HORIZONTAL, 
            length=200,
            command=self.format_webp_quality_value
        )
        self.webp_quality_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Label(self.webp_quality_frame, textvariable=self.webp_quality_display_value).pack(side=tk.LEFT, padx=5)  # 표시용 변수 사용
        ttk.Label(self.webp_quality_frame, text="(LOW ← → HIGH)").pack(side=tk.LEFT)
        
        # 처음에는 PNG가 선택되므로 PNG 압축 설정만 표시
        self.jpeg_quality_frame.pack_forget()
        self.png_compression_frame.pack(fill=tk.X)
        self.webp_quality_frame.pack_forget()
        
        # 변환 버튼 및 진행 영역
        control_frame = ttk.Frame(main_frame, padding="10")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.convert_button = ttk.Button(control_frame, text="변환 시작", command=self.start_conversion)
        self.convert_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(control_frame, text="취소", command=self.cancel_conversion, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        # 진행 상황 표시용
        progress_frame = ttk.LabelFrame(main_frame, text="진행 상황", padding="10")
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(progress_frame, text="현재 파일:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(progress_frame, textvariable=self.current_file).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(progress_frame, text="진행률:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_value, maximum=100)
        self.progress_bar.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="대기 중...")
        self.status_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        progress_frame.columnconfigure(1, weight=1)
        
        # 로그 영역
        log_frame = ttk.LabelFrame(main_frame, text="변환 로그", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, width=50, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        self.log_text.config(state=tk.DISABLED)





#소수점 1자리로 tkinter UI에 보내고 실제값은 따로 변수 만들어서 품질에 적용

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
    






    '''tkinter UI 사이즈 조절'''
    def toggle_resize(self):
        if self.resize_enabled.get():
            self.resize_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        else:
            self.resize_frame.pack_forget()
    





    def on_format_changed(self, event):
        selected_format = self.output_format.get()
        
        #숨기기
        self.jpeg_quality_frame.pack_forget()
        self.png_compression_frame.pack_forget()
        self.webp_quality_frame.pack_forget()
        
        # 어떤 품질 선택했는지에 따라서 해당 설정 표시
        if "JPEG" in selected_format:
            self.jpeg_quality_frame.pack(fill=tk.X)
            self.quality_value.set(self.format_quality_settings["jpg"])
        elif "PNG" in selected_format:
            self.png_compression_frame.pack(fill=tk.X)
            self.compression_value.set(self.format_quality_settings["png"])
        elif "WebP" in selected_format:
            self.webp_quality_frame.pack(fill=tk.X)
            self.quality_value.set(self.format_quality_settings["webp"])











    
    def browse_input_folder(self):
        folder = filedialog.askdirectory(title="JP2 파일이 있는 폴더 선택")
        if folder:
            self.input_folder.set(folder)
            if not self.output_folder.get():
                self.output_folder.set(os.path.join(folder, "converted"))
    
    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="변환된 이미지를 저장할 폴더 선택")
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
            messagebox.showerror("오류", "입력 폴더를 선택해주세요.")
            return
        
        if not self.output_folder.get():
            messagebox.showerror("오류", "출력 폴더를 선택해주세요.")
            return
        
        # 출력 폴더가 없으면 생성
        if not os.path.exists(self.output_folder.get()):
            os.makedirs(self.output_folder.get())
        
        # 출력 형식 설정
        format_mapping = {
            "PNG (.png) - 무손실 압축": "png",
            "JPEG (.jpg) - 손실 압축, 작은 파일 크기": "jpg",
            "TIFF (.tiff) - 무손실 또는 손실 압축": "tiff",
            "BMP (.bmp) - 무압축, 큰 파일 크기": "bmp",
            "WebP (.webp) - 웹용 이미지 형식": "webp"
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
            messagebox.showinfo("정보", "입력 폴더에 JP2 파일이 없습니다.")
            return
        
        self.file_count.set(len(jp2_files))
        self.processed_count.set(0)
        self.progress_value.set(0)
        
        # UI 상태 업데이트
        self.convert_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.status_label.config(text=f"변환 중... (0/{self.file_count.get()})")
        self.processing = True
        
        # 로그 초기화
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        
        # 품질 설정 로깅
        quality_info = ""
        if selected_format == "jpg":
            quality_info = f", 품질: {self.format_quality_settings['jpg']}%"
        elif selected_format == "png":
            quality_info = f", 압축: {self.format_quality_settings['png']}"
        elif selected_format == "webp":
            quality_info = f", 품질: {self.format_quality_settings['webp']}%"
        
        self.log(f"변환 시작: {len(jp2_files)}개의 JP2 파일을 {selected_format.upper()} 형식으로 변환합니다{quality_info}.")
        
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
                    self.root.after(0, lambda path=input_path: self.log(f"오류: {path} 파일을 읽을 수 없습니다."))
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
                    self.root.after(0, lambda path=input_path: self.log(f"오류: {path} 파일을 인코딩할 수 없습니다."))
                
            except Exception as e:
                error_msg = f"파일 변환 중 오류 발생: {input_path}\n오류 메시지: {str(e)}"
                self.root.after(0, lambda msg=error_msg: self.log(msg))
        
        # 변환 완료 후 UI 업데이트
        self.root.after(0, self.conversion_completed)
    
    def update_progress(self, current_idx, total_files, input_path, output_path):
        self.processed_count.set(current_idx + 1)
        progress_percent = ((current_idx + 1) / total_files) * 100
        self.progress_value.set(progress_percent)
        self.status_label.config(text=f"변환 중... ({current_idx + 1}/{total_files})")
        self.log(f"변환: {input_path} -> {output_path}")
    
    def conversion_completed(self):
        if self.processing:
            self.log(f"변환 완료: {self.processed_count.get()}개의 파일이 변환되었습니다.")
            messagebox.showinfo("완료", f"모든 파일 변환이 완료되었습니다.\n총 {self.processed_count.get()}개의 파일이 변환되었습니다.")
        else:
            self.log("변환이 사용자에 의해 취소되었습니다.")
        
        # UI 상태 초기화
        self.processing = False
        self.convert_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.status_label.config(text="기다리는 중...")
        self.current_file.set("")
    
    def cancel_conversion(self):
        if messagebox.askyesno("취소", "변환을 취소하시겠습니까?"):
            self.processing = False

if __name__ == "__main__":
    root = tk.Tk()
    app = jp2convert_func(root)
    root.mainloop()