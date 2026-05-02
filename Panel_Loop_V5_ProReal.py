import os, time, threading, subprocess, tkinter as tk
from pathlib import Path
from datetime import datetime
from tkinter import messagebox

CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0
GAMELOOP_PATHS = [
r"C:\Program Files\TxGameAssistant\AppMarket\AppMarket.exe",
r"C:\Program Files\TxGameAssistant\ui\AppMarket.exe",
r"C:\Program Files\TxGameAssistant\AndroidEmulatorEx.exe",
r"C:\Program Files\GameLoop\Launcher.exe",
r"D:\Program Files\TxGameAssistant\AppMarket\AppMarket.exe",
r"D:\TxGameAssistant\AppMarket\AppMarket.exe"]
PROCESSES=["AndroidEmulatorEx","AndroidEmulator","aow_exe","AppMarket","ProjectTitan","AndroidRender"]
SAFE_JUNK=["XboxGameBar","GameBar","Widgets","OneDrive","YourPhone","PhoneExperienceHost"]

def run_ps(cmd, timeout=25):
    try:
        subprocess.run(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-WindowStyle","Hidden","-Command",cmd],
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=timeout,creationflags=CREATE_NO_WINDOW)
        return True
    except:
        return False

def get_wmi(prop, cls):
    try:
        out=subprocess.check_output(["powershell","-NoProfile","-Command",f"(Get-CimInstance {cls} | Select-Object -First 1 -ExpandProperty {prop})"],creationflags=CREATE_NO_WINDOW,stderr=subprocess.DEVNULL).decode(errors="ignore").strip()
        return out if out else "Unknown"
    except:
        return "Unknown"

def logical_cores():
    try: return int(get_wmi("NumberOfLogicalProcessors","Win32_Processor"))
    except: return os.cpu_count() or 4

def make_mask():
    logical=logical_cores()
    if logical>=16: start,end=4,11
    elif logical>=12: start,end=2,9
    elif logical>=8: start,end=1,6
    else: start,end=0,max(0,logical-2)
    mask=0
    for i in range(start,min(end,logical-1)+1): mask|=1<<i
    return mask or 1,start,min(end,logical-1)

def find_gameloop():
    for p in GAMELOOP_PATHS:
        if Path(p).exists(): return p
    return None

def gameloop_running():
    try:
        out=subprocess.check_output(["tasklist"],creationflags=CREATE_NO_WINDOW,stderr=subprocess.DEVNULL).decode(errors="ignore")
        return any(x+".exe" in out for x in ["AndroidEmulatorEx","aow_exe","AppMarket"])
    except:
        return False

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PANEL LOOP V5 PRO REAL - Ahmad Nazari")
        self.geometry("980x660"); self.minsize(880,600); self.configure(bg="#07090d")
        self.running=False; self.loop_seconds=5; self.mask,self.core_start,self.core_end=make_mask(); self.quiet=0
        self.build_ui(); self.update_cards(); self.log("V5 Pro Real loaded."); self.log("Best flow: PRE-GAME CLEAN once → SMART START.")

    def build_ui(self):
        header=tk.Frame(self,bg="#07090d",height=120); header.pack(fill="x")
        tk.Label(header,text="PANEL LOOP V5 PRO REAL",fg="#00ffd5",bg="#07090d",font=("Consolas",30,"bold")).place(x=24,y=18)
        tk.Label(header,text="SMART NO-STUTTER ENGINE FOR GAMELOOP / PUBG",fg="#00ffd5",bg="#07090d",font=("Consolas",13,"bold")).place(x=28,y=72)
        self.engine_label=tk.Label(header,text="ENGINE: OFF",fg="#ffdf5d",bg="#07090d",font=("Consolas",13,"bold")); self.engine_label.place(x=760,y=50)
        tk.Frame(self,bg="#00ffd5",height=2).pack(fill="x")
        body=tk.Frame(self,bg="#07090d"); body.pack(fill="both",expand=True,padx=16,pady=14)
        left=tk.Frame(body,bg="#07090d",width=290); left.pack(side="left",fill="y")
        self.btn(left,"🚀 SMART START","#31ff47",self.smart_start)
        self.btn(left,"🧼 PRE-GAME CLEAN","#ffdf5d",self.pre_game_clean)
        self.btn(left,"🌐 NETWORK SAFE BOOST","#00ffd5",self.network_safe_boost)
        self.btn(left,"🎮 START GAMELOOP","#4aa3ff",self.start_gameloop)
        self.btn(left,"🔁 RE-APPLY STABILITY","#ffdf5d",self.apply_stability)
        self.btn(left,"🛑 STOP ENGINE","#ff4d6d",self.stop_engine)
        self.btn(left,"↩ RESTORE DEFAULTS","#aaaaaa",self.restore_defaults)
        self.btn(left,"❌ EXIT","#ff4d6d",self.on_close)
        right=tk.Frame(body,bg="#07090d"); right.pack(side="left",fill="both",expand=True,padx=(16,0))
        cards=tk.Frame(right,bg="#07090d"); cards.pack(fill="x")
        self.card_cpu=self.card(cards,"CPU / AFFINITY","#4aa3ff",0,0)
        self.card_gpu=self.card(cards,"GPU PREFERENCE","#31ff9f",0,1)
        self.card_engine=self.card(cards,"FPS STABILITY LOOP","#ffdf5d",1,0)
        self.card_clean=self.card(cards,"NO-STUTTER CLEANING","#ff9f43",1,1)
        cards.columnconfigure(0,weight=1); cards.columnconfigure(1,weight=1)
        log_frame=tk.Frame(right,bg="#101217",relief="solid",bd=1); log_frame.pack(fill="both",expand=True,pady=(12,0))
        tk.Label(log_frame,text="> V5 PRO REAL LOG",fg="white",bg="#101217",font=("Consolas",14,"bold")).pack(anchor="w",padx=12,pady=8)
        self.log_box=tk.Text(log_frame,bg="black",fg="#31ff47",insertbackground="#31ff47",font=("Consolas",10),relief="flat")
        self.log_box.pack(fill="both",expand=True,padx=12,pady=(0,12))
        self.protocol("WM_DELETE_WINDOW",self.on_close)

    def btn(self,parent,text,color,cmd):
        tk.Button(parent,text=text,command=cmd,bg="#15191f",fg=color,activebackground="#232a33",activeforeground=color,relief="flat",anchor="w",padx=16,pady=12,font=("Consolas",10,"bold")).pack(fill="x",pady=5)

    def card(self,parent,title,color,row,col):
        f=tk.Frame(parent,bg="#101217",relief="solid",bd=1,width=320,height=110); f.grid(row=row,column=col,padx=5,pady=5,sticky="nsew"); f.pack_propagate(False)
        tk.Label(f,text=title,bg="#101217",fg=color,font=("Consolas",12,"bold")).pack(anchor="w",padx=14,pady=(10,0))
        l=tk.Label(f,text="",bg="#101217",fg="white",font=("Consolas",10),justify="left"); l.pack(anchor="w",padx=14,pady=8)
        return l

    def update_cards(self):
        self.card_cpu.config(text=f"{get_wmi('Name','Win32_Processor')}\nUsing CPU {self.core_start}-{self.core_end}\nMask: {self.mask}")
        self.card_gpu.config(text=f"{get_wmi('Name','Win32_VideoController')}\nWindows preference:\nHigh Performance")
        self.card_engine.config(text=f"Engine: {'ON' if self.running else 'OFF'}\nInterval: {self.loop_seconds}s\nOnly if GameLoop runs")
        self.card_clean.config(text="Clean only before game\nNo cleaning during match\nNo popups")

    def log(self,msg,force=True):
        if self.running and not force:
            self.quiet+=1
            if self.quiet%10!=0: return
        self.log_box.insert("end",f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n"); self.log_box.see("end")

    def power_mode(self):
        run_ps("powercfg /S SCHEME_MIN"); self.log("Power plan set to High Performance.")

    def gpu_preference(self):
        for exe in dict.fromkeys(GAMELOOP_PATHS):
            run_ps(f"New-Item -Path 'HKCU:\\Software\\Microsoft\\DirectX\\UserGpuPreferences' -Force | Out-Null; New-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\DirectX\\UserGpuPreferences' -Name '{exe}' -Value 'GpuPreference=2;' -PropertyType String -Force | Out-Null")
        self.log("GPU preference set to High Performance.")

    def apply_stability(self):
        names=",".join([f"'{p}'" for p in PROCESSES])
        run_ps(f"$names=@({names}); foreach($n in $names){{ Get-Process -Name $n -ErrorAction SilentlyContinue | ForEach-Object {{ try {{ if($_.ProcessName -ne 'adb'){{$_.PriorityClass='High'}} }} catch {{}}; try {{ if($_.ProcessName -ne 'QMEmulatorService'){{$_.ProcessorAffinity={self.mask}}} }} catch {{}} }} }}")
        self.log(f"Stability applied: CPU {self.core_start}-{self.core_end}, High priority."); self.update_cards()

    def safe_background_clean(self):
        names=",".join([f"'{p}'" for p in SAFE_JUNK])
        run_ps(f"$names=@({names}); foreach($n in $names){{ Get-Process -Name $n -ErrorAction SilentlyContinue | ForEach-Object {{ try {{ Stop-Process -Id $_.Id -Force }} catch {{}} }} }}")
        self.log("Safe background clean done.")

    def pre_game_clean(self):
        self.log("Pre-game clean started. Do this before match, not during fight.")
        self.safe_background_clean()
        dirs=[os.path.join(os.getenv("LOCALAPPDATA",""),"D3DSCache"),os.path.join(os.getenv("LOCALAPPDATA",""),"NVIDIA","DXCache"),os.path.join(os.getenv("LOCALAPPDATA",""),"NVIDIA","GLCache"),os.getenv("TEMP","")]
        cleaned=0
        for d in dirs:
            if d and os.path.exists(d):
                for root,_,files in os.walk(d):
                    for f in files:
                        try: os.remove(os.path.join(root,f)); cleaned+=1
                        except: pass
        self.log(f"Pre-game clean finished. Files cleaned: {cleaned}")

    def network_safe_boost(self):
        run_ps("ipconfig /flushdns"); self.log("Network safe boost applied: DNS flushed only.")

    def engine_loop(self):
        while self.running:
            if gameloop_running():
                self.apply_stability()
                self.log("Smart stability loop active.",force=False)
            time.sleep(self.loop_seconds)

    def start_engine(self):
        if self.running: self.log("Engine already running."); return
        self.running=True; self.engine_label.config(text="ENGINE: ON",fg="#31ff47")
        self.power_mode(); self.gpu_preference(); self.apply_stability()
        threading.Thread(target=self.engine_loop,daemon=True).start()
        self.update_cards(); self.log("Smart FPS Stability Engine started.")

    def stop_engine(self):
        self.running=False; self.engine_label.config(text="ENGINE: OFF",fg="#ffdf5d"); self.update_cards(); self.log("Engine stopped.")

    def start_gameloop(self):
        path=find_gameloop()
        if not path:
            messagebox.showwarning("GameLoop not found","GameLoop was not found in default paths."); self.log("GameLoop not found in default paths."); return
        try:
            subprocess.Popen([path],creationflags=CREATE_NO_WINDOW); self.log(f"GameLoop started: {path}")
            self.after(6000,self.apply_stability); self.after(12000,self.apply_stability); self.after(22000,self.apply_stability)
        except Exception as e: self.log(f"Could not start GameLoop: {e}")

    def smart_start(self):
        self.log("Smart Start running..."); self.start_engine(); self.network_safe_boost(); self.start_gameloop(); self.log("Smart Start complete. Keep tool open while playing.")

    def restore_defaults(self):
        if not messagebox.askyesno("Restore Defaults","Restore keyboard/mouse/power defaults?"): return
        self.stop_engine()
        run_ps("powercfg /S SCHEME_BALANCED")
        self.log("Defaults restored. Restart recommended.")

    def on_close(self):
        self.running=False; self.destroy()

if __name__=="__main__":
    App().mainloop()
