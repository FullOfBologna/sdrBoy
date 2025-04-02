# SDR Gameboy Cartridge
This is a project inspired by the (GBDSO)[https://www.mikrocontroller.net/attachment/7239/gbdso_uk.pdf] project by Steve Willis in 2000. 

First, I am implementing a python based GameBoy emulator as a 2 fold learning opportunity. I want to learn python more in depth, and I want to learn the ins and out of the Game Boy and development in Assembly. 

(I understand I will likely eventually run into performance issues and will need to switch to hardware) 
I am targetting learning only the earliest model of the game boy to start. End goal would be to implement this hardware on a gameboy color.

As this grows I will likely become more open to contributions. Initially this is just a pet project to keep the mind sharp. 

## Roadmap 
1. [ ] Implement Gameboy emulator & Screen Rendering Engine from Scratch
2. [ ] Write debugger tools in emulator gui
3. [ ] Run a comprehensive Test ROM
4. [ ] Begin development of SDR ROM with simulated FFT data
5. [ ] Start PCB Layout of SDR using RTL-SDR as inspiration, and modifying layout into game boy cartridge PCB
6. [ ] Figure out how to handle the processing of the digitized data from the sdr, and how to pipe the data into the game boy for rendering. 
   
