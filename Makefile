#all:
#	python3 pasm.py helloworld.asm > helloworld2.asm
#	dasm helloworld2.asm -ohello.prg
#	c1541 -format "1234,01" d64 hello.d64
#	# using 1234 because I can't figure out petscii
#	c1541 hello.d64 -write hello.prg "1234"	

%.d64: %.asm
	python3 pasm.py $< > $*_2.asm
	dasm $*_2.asm -o$*.prg
	c1541 -format "1234,01" d64 $*.d64
	c1541 $*.d64 -write $*.prg "1234"	
