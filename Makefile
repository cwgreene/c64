all:
	dasm helloworld.asm -ohello.prg
	c1541 -format "1234,01" d64 hello.d64
	# using 1234 because I can't figure out petscii
	c1541 hello.d64 -write hello.prg "1234"	
