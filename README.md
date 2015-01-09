# DARC_tool
easy Nintendo 3DS DARC container unpack/inject tool

Feature:

-support texture  data alignment (bcfnt & bclim)

-support inject mode : extend new file at the end of darc archives (using -inject option)

-support bcfnt batch import mode (for Theatrhythm Final Fantasy)

usage :

              unpack darc files : DARC_tool -unpack 123.arc
              
              inject darc files : DARC_tool -inject 123.arc
              
              repack darc files : DARC_tool -pack 123.arc
              
bcfnt_plugin.py is a useful plugin for quick copy same bcfnt font files to all darc archives

 
2015.1.9
