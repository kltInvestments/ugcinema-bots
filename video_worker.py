import subprocess, shlex

def overlay_style_A(input_path: str, output_path: str, title: str, cta: str|None, preset: str="veryfast"):
    safe_title = title.replace("'", "\'")
    draw_top = f"drawbox=x=0:y=0:w=iw:h=80:color=black@0.7:t=max,drawtext=text='{safe_title}':fontcolor=white:fontsize=28:x=(w-text_w)/2:y=20"
    draw_bottom = ""
    if cta:
        safe_cta = cta.replace("'", "\'")
        draw_bottom = f",drawbox=x=0:y=h-80:w=iw:h=80:color=black@0.7:t=max,drawtext=text='{safe_cta}':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=h-60"
    vf = f"scale=1280:-2,{draw_top}{draw_bottom}"
    cmd = f"ffmpeg -y -i {shlex.quote(input_path)} -vf {shlex.quote(vf)} -c:v libx264 -preset {preset} -crf 23 -c:a copy {shlex.quote(output_path)}"
    subprocess.run(cmd, shell=True, check=True)
