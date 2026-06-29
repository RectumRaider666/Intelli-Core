#!/bin/python3

VERSION = '0.4.7'
DESC = 'Media 2 Media - Batch Convert different Media formats to other formats by path CLI or Entire Folders'
DEPS = [{"Py": ['pillow', 'tqdm', 'svglib']}, {"Shell": ['ffmpeg']}]

# <!-- [SS-1]: Dependencies ----->
import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from PIL import Image
from tqdm import tqdm
import json
import argparse
import subprocess

# <!-- [SS-2]: Global Variables ----->
_dir = os.path.dirname(os.path.abspath(__file__))
_res = os.path.join(_dir, 'out')
_usr = os.path.expanduser('~')
MEDIA_EXT = {
    'image': ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif', '.webp', '.jfif', '.heic', '.heif', '.avif', '.tga', '.dds'],
    'icons': ['.ico', '.svg', '.eps'],
    'audio': ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma', '.opus', '.aiff'],
    'video': ['.mp4', '.mov', '.wmv', '.avi', '.mkv', '.webm', '.flv', '.m4v', '.mpg', '.mpeg', '.3gp', '.ogv']
}

# <!-- [SS-3]: Functions ----->
# /3.1/: Compatibility Check Function
def compat (tar:str, in_file:str, out_file:str, on:bool) -> tuple[list[str], list[str], str|None]:
    """
    Creates a list of all the files which are compatible for conversion and those which are not.
    Is not recursive, files inside sub folders will be ignored.
    Use this to see which ones the script is dropping and manually convert them later if needed.
    Returns: (compatible_files, non_compatible_files, media_type)
    Args: tar=target_dir, in_file=to_convert_ext, out_file=converted_ext, on=list_compatilities
    """
    global comp, cc, nc, media_type
    comp: list[str] = []
    non_comp: list[str] = []
    cc:int = 0
    nc:int = 0
    in_ext = f'.{in_file}'
    media_type: str|None = None
    for category, extensions in MEDIA_EXT.items():
        if in_ext in extensions:
            media_type = category
            break
    if media_type is None:
        print(f'[ERROR] The input file type .{in_file} is not supported.')
        return comp, non_comp, None
    for item in os.listdir(tar):
        item_path = os.path.join(tar, item)
        if os.path.isdir(item_path):  # Skip directories
            continue
        test = os.path.splitext(item_path)
        if test[1].lower() == f'.{in_file}':
            comp.append(item_path)
            cc += 1
        else:
            non_comp.append(item_path)
            nc += 1
    if on:
        with open(os.path.join(_res, 'comps.log'), 'w') as cf:
            cf.write(f"{cc} Compatible and {nc} Non-Compatible files for conversion from {in_file} to {out_file}\n")
            cf.write(f"Media Type: {media_type}\n\n[Compatible]\n")
            for i in comp:
                cf.write(f'{i}\n')
            cf.write(f"\n[Non-Compatible]\n")
            for i in non_comp:
                cf.write(f'{i}\n')
    return comp, non_comp, media_type

# /3.2/: Conversion Function
def convert (dest:str, in_file:str, out_file:str, dlt:bool=False) -> None:
    """
    Converts all var:cc<num> files listed in var:comp into out_file format in the var:dest folder
    media_type: The category of media (image, icons, audio, video)
    dlt will delete the original files after conversion if set to True
    """
    # /3.2.1/: Setup
    in_ext = f'.{in_file}'
    print(f"Converting {cc} {media_type} files from .{in_file} to .{out_file}")
    os.makedirs(dest, exist_ok=True)
    for item in tqdm(comp, desc="Converting Files", unit="file"):
        base = os.path.basename(item)
        name = os.path.splitext(base)[0]
        out_path = os.path.join(dest, f'{name}.{out_file}')
        ext = os.path.splitext(item)[1].lower()
        if ext != in_ext:
            print(f"[WARN] Skipping {item} - expected {in_ext}, got {ext}")
            continue
        try:

    # /3.2.2/: Image
            if media_type == 'image':
                with Image.open(item) as img:
                    no_alpha_formats = ['jpg', 'jpeg', 'jfif', 'bmp']
                    if out_file.lower() in no_alpha_formats and img.mode in ['RGBA', 'LA', 'P']:
                        if img.mode == 'P' and 'transparency' in img.info:
                            img = img.convert('RGBA')
                        if img.mode in ['RGBA', 'LA']:
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'RGBA':
                                background.paste(img, mask=img.split()[3])
                            else:
                                background.paste(img, mask=img.split()[1])
                            img = background
                    save_kwargs = {}
                    if out_file.lower() in ['jpg', 'jpeg', 'jfif']:
                        save_kwargs['quality'] = 95
                        save_kwargs['optimize'] = True
                    elif out_file.lower() == 'webp':
                        save_kwargs['quality'] = 95
                        save_kwargs['method'] = 6
                    elif out_file.lower() == 'png':
                        save_kwargs['optimize'] = True
                    try:
                        img.save(out_path, format=out_file.upper(), **save_kwargs)
                    except (OSError, ValueError) as save_err:
                        print(f"[WARN] Direct save failed for {out_file}, trying basic save: {save_err}")
                        img.save(out_path, format=out_file.upper())

    # /3.2.3/: Icons
            elif media_type == 'icons':
                icon_sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
                if ext in ['.svg', '.eps']:
                    drawing = svg2rlg(item)
                    if drawing is None:
                        raise Exception(f"Failed to parse vector file: {item}")
                    if out_file.lower() == 'ico':
                        temp_png = out_path.replace('.ico', '_temp.png')
                        renderPM.drawToFile(drawing, temp_png, fmt='PNG')  # type: ignore
                        with Image.open(temp_png) as img:
                            img.save(out_path, format='ICO', sizes=icon_sizes)
                        os.remove(temp_png)
                    else:
                        renderPM.drawToFile(drawing, out_path, fmt=out_file.upper())  # type: ignore
                else:
                    with Image.open(item) as img:
                        if out_file.lower() == 'ico':
                            img.save(out_path, format='ICO', sizes=icon_sizes)
                        else:
                            img.save(out_path)

    # /3.2.4/: Audio
            elif media_type == 'audio':
                ffmpeg_cmd = ['ffmpeg', '-i', item, '-y']
                if out_file.lower() == 'mp3':
                    ffmpeg_cmd.extend(['-codec:a', 'libmp3lame', '-b:a', '320k'])
                elif out_file.lower() == 'aac' or out_file.lower() == 'm4a':
                    ffmpeg_cmd.extend(['-codec:a', 'aac', '-b:a', '256k'])
                elif out_file.lower() == 'flac':
                    ffmpeg_cmd.extend(['-codec:a', 'flac', '-compression_level', '8'])
                elif out_file.lower() == 'opus':
                    ffmpeg_cmd.extend(['-codec:a', 'libopus', '-b:a', '192k'])
                elif out_file.lower() == 'ogg':
                    ffmpeg_cmd.extend(['-codec:a', 'libvorbis', '-q:a', '8'])
                elif out_file.lower() == 'wav':
                    ffmpeg_cmd.extend(['-codec:a', 'pcm_s16le'])
                elif out_file.lower() == 'aiff':
                    ffmpeg_cmd.extend(['-codec:a', 'pcm_s16be'])
                elif out_file.lower() == 'wma':
                    ffmpeg_cmd.extend(['-codec:a', 'wmav2', '-b:a', '192k'])
                ffmpeg_cmd.append(out_path)
                result = subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                if result.returncode != 0:
                    raise Exception(f"ffmpeg failed: {result.stderr.decode()}")

    # /3.2.5/: Video
            elif media_type == 'video':
                ffmpeg_cmd = ['ffmpeg', '-i', item, '-y']
                if out_file.lower() == 'mp4':
                    ffmpeg_cmd.extend(['-codec:v', 'libx264', '-crf', '18', '-preset', 'slow', '-codec:a', 'aac', '-b:a', '256k'])
                elif out_file.lower() == 'webm':
                    ffmpeg_cmd.extend(['-codec:v', 'libvpx-vp9', '-crf', '30', '-b:v', '0', '-codec:a', 'libopus', '-b:a', '192k'])
                elif out_file.lower() == 'mkv':
                    ffmpeg_cmd.extend(['-codec:v', 'libx264', '-crf', '18', '-preset', 'slow', '-codec:a', 'aac', '-b:a', '256k'])
                elif out_file.lower() == 'avi':
                    ffmpeg_cmd.extend(['-codec:v', 'libx264', '-crf', '18', '-codec:a', 'mp3', '-b:a', '320k'])
                elif out_file.lower() == 'mov':
                    ffmpeg_cmd.extend(['-codec:v', 'libx264', '-crf', '18', '-preset', 'slow', '-codec:a', 'aac', '-b:a', '256k'])
                elif out_file.lower() == 'm4v':
                    ffmpeg_cmd.extend(['-codec:v', 'libx264', '-crf', '18', '-codec:a', 'aac', '-b:a', '256k'])
                elif out_file.lower() == 'flv':
                    ffmpeg_cmd.extend(['-codec:v', 'flv', '-codec:a', 'mp3', '-b:a', '128k'])
                elif out_file.lower() == 'wmv':
                    ffmpeg_cmd.extend(['-codec:v', 'wmv2', '-b:v', '5000k', '-codec:a', 'wmav2', '-b:a', '192k'])
                elif out_file.lower() in ['mpg', 'mpeg']:
                    ffmpeg_cmd.extend(['-codec:v', 'mpeg2video', '-b:v', '5000k', '-codec:a', 'mp2', '-b:a', '192k'])
                elif out_file.lower() == '3gp':
                    ffmpeg_cmd.extend(['-codec:v', 'h263', '-b:v', '500k', '-codec:a', 'aac', '-b:a', '64k', '-s', '320x240'])
                elif out_file.lower() == 'ogv':
                    ffmpeg_cmd.extend(['-codec:v', 'libtheora', '-q:v', '7', '-codec:a', 'libvorbis', '-q:a', '5'])
                ffmpeg_cmd.append(out_path)
                result = subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                if result.returncode != 0:
                    raise Exception(f"ffmpeg failed: {result.stderr.decode()}")

    # /3.2.6/: Cleanup
            if dlt:
                os.remove(item)
        except Exception as e:
            print(f"\n[ERROR] Failed to convert {item}: {e}")
            continue

# <!-- [SS-4]: RUNNIT ----->
if __name__ == "__main__":
    # /4.1/: Prepare
    with open(os.path.join(_dir, 'set.jsonc'), 'r') as ml:
        raw = json.load(ml)
        config:dict[str, str] = raw['m2m']
    p = argparse.ArgumentParser(description=DESC)
    p.add_argument('--version', action='version', version=f'%(prog)s {VERSION}\n {DESC}\n')
    p.add_argument('--int', type=str, help='The input file type to convert from', default="webp")
    p.add_argument('--out', type=str, help='The output file type to convert to', default="png")
    p.add_argument('--dir', type=str, help='The path to the file or folder to convert', default=os.path.join(_usr, 'Pictures'))
    p.add_argument('--res', type=str, help='The output folder to save converted files', default=_res)
    p.add_argument('--dlt', action='store_true', help='Delete original files after conversion toggle', default=False)
    p.add_argument('--lst', action='store_true', help='Save compatible and non-compatible files toggle', default=True)
    args = p.parse_args()

# /4.2/: No args
    if args.int is None and args.out is None and args.dir is None:
        print("[INFO] Using settings from set.jsonc")
        comp_files, non_comp_files, m_type = compat(
            tar=config['Input Dir'],
            in_file=config['Mime-Type'],
            out_file=config['Out Type'],
            on=bool(config['Comps'])
        )
        if m_type is not None and len(comp_files) > 0:
            convert(
                dest=config['Output Dir'],
                in_file=config['Mime-Type'],
                out_file=config['Out Type'],
                dlt=bool(config['Delete'])
            )
        else:
            print("[INFO] No compatible files found for conversion.")

# /4.3/: Args
    elif args.int and args.out and args.dir:
        print("[INFO] Using CLI arguments")
        comp_files, non_comp_files, m_type = compat(
            tar=args.dir,
            in_file=args.int,
            out_file=args.out,
            on=args.lst
        )
        if m_type is not None and len(comp_files) > 0:
            convert(
                dest=args.res if args.res else _res,
                in_file=args.int,
                out_file=args.out,
                dlt=args.dlt
            )
        else:
            print("[INFO] No compatible files found for conversion.")
    else:
        print("[ERROR] Missing required arguments: --int, --out, and --dir")
        p.print_help()

# <!-- [SS-X]: Usage ----->
CLI=[
    "python3 m2m.py --int req:<in_file> --out req:<out_file> --dir req:<address> --res opt <output dir> --dlt opt:<bool> --lst opt:<bool>",
    "python3 m2m.py --int webp --out png --dir /path/to/input/folder --res /path/to/output/folder --dlt False --lst True",
]
