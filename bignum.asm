    processor 6502         ; Specify the 6502 processor type
    org $0801              ; Program starting address (C64 BASIC start)

    ; C64 BASIC Program Header
    byte $0C,$08,$40,$00,$9E,$20,$32,$30,$36,$32,$00,$00,$00
    jsr $E544
    ldx #$00

    ; Set up screen memory location and text
    ldx #0                 ; Start index at 0
loop:
    lda message,x         ; Load the message character by character
    beq end                ; If the character is null (0), end loop
    sta $0400,x           ; Store character in screen memory ($0400 = top-left corner of C64 screen)
    inx                    ; Increment index
    bne loop               ; Repeat until the end of message

end:
    rts                    ; Return from subroutine

message:
    .byte {{ "HELLO WORLD!" | screencode }},0
