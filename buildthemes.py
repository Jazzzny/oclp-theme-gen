# Icon generation script
# Copyright © 2023 Jazzzny

import os
import subprocess
import sys
import plistlib
import shutil
from distutils.dir_util import copy_tree

try:
    subprocess.check_output(["convert"])
except FileNotFoundError:
        raise Exception("ImageMagick is not installed or set in the PATH.")
try:
    subprocess.call(["icnspack"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT)
except FileNotFoundError:
        raise Exception("icnspack is not installed or set in the PATH.")

curpath = os.path.abspath(os.getcwd())

print("Entering icon assets folder")
os.chdir(sys.path[0])

try:
    os.mkdir("BaseIcons_Padded")
except:
    pass

try:
    os.mkdir("PNGOut")
except:
    pass

try:
    os.mkdir("CompiledThemes")
except:
    pass

try:
    os.mkdir("Output")
except:
    pass

for filename in os.listdir("BaseIcons"):
    f = os.path.join("BaseIcons", filename)
    if os.path.isfile(f) and f.endswith('.png'):
        print(f"Preparing {filename}")
        subprocess.run([
            "convert",f,
            "-resize","472x472",
            "-background","none",
            "-gravity","center",
            "-extent","512x512",
            "-filter","Lanczos",
            f"BaseIcons_Padded/{filename}"])

for theme in os.listdir("Themes"):
    if theme == ".DS_Store":
        continue
    if os.path.isfile(f"Themes/{theme}/theme.plist"):
        with open(f"Themes/{theme}/theme.plist", 'rb') as plist_file:
            plist_data = plistlib.load(plist_file)
        print(f"===========================\nCreating {plist_data['ThemeName']}\n===========================")

        try:
            os.mkdir(f"PNGOut/{theme}")
        except:
            pass

        try:
            os.mkdir(f"CompiledThemes/{theme}")
            shutil.copy(f"Themes/{theme}/theme.plist",f"CompiledThemes/{theme}/theme.plist")
            copy_tree(f"Themes/{theme}/BaseTheme",f"CompiledThemes/{theme}")
        except:
            pass

        for mask in os.listdir(f"Themes/{theme}"):
            if mask.endswith('.png'):
                print(f"Processing icons for {mask}")
                for filename in os.listdir("BaseIcons_Padded"):
                    subprocess.run([
                        "convert",
                        "-background","none",
                        f"{os.path.join('BaseIcons_Padded', filename)}",
                        f"{os.path.join(f'Themes/{theme}', mask)}",
                        "-gravity","center",
                        "-geometry",plist_data["MaskFiles"][mask],
                        "-composite",
                        "-resize","256x256",
                        "-filter","Lanczos",
                        f"PNGOut/{theme}/{mask.split('.')[0]}{filename.split('.')[0]}_2x.png"
                    ])
                    subprocess.run([
                        "convert",
                        "-background","none",
                        f"{os.path.join('BaseIcons_Padded', filename)}",
                        f"{os.path.join(f'Themes/{theme}', mask)}",
                        "-gravity","center",
                        "-geometry",plist_data["MaskFiles"][mask],
                        "-composite",
                        "-resize","128x128",
                        "-filter","Lanczos",
                        f"PNGOut/{theme}/{mask.split('.')[0]}{filename.split('.')[0]}_1x.png"
                    ])
                    subprocess.run([
                        "icnspack",
                        f"CompiledThemes/{theme}/{mask.split('.')[0]}{filename.split('.')[0]}.icns",
                        f"PNGOut/{theme}/{mask.split('.')[0]}{filename.split('.')[0]}_1x.png",
                        f"PNGOut/{theme}/{mask.split('.')[0]}{filename.split('.')[0]}_2x.png"
                    ])

for compiledtheme in os.listdir("CompiledThemes"):
    print(f"===========================\nCompressing {compiledtheme}\n===========================")
    shutil.make_archive(f"Output/{compiledtheme}", 'zip', f"CompiledThemes/{compiledtheme}")
    os.rename(f"Output/{compiledtheme}.zip",f"Output/{compiledtheme}.oclptheme")

shutil.make_archive("Themes", 'zip', "Output")

print("Removing temporary directories")
shutil.rmtree("BaseIcons_Padded")
shutil.rmtree("PNGOut")
shutil.rmtree("CompiledThemes")
shutil.rmtree("Output")

print("Returning to original folder")
os.chdir(curpath)