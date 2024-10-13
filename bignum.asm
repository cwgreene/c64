    processor 6502         ; Specify the 6502 processor type
    org $0801              ; Program starting address (C64 BASIC start)

    ; C64 BASIC Program Header
    byte $0C,$08,$40,$00,$9E,$20,$32,$30,$36,$32,$00,$00,$00
    jsr $E544
    ldx #$00

    ; Set up screen memory location and text
    ldx #0                 ; Start index at 0
    jmp add

; we're going to use 0x1000 for a,b,c
loadbig_a:
    ; TODO: use X to select page, Y to select offset in page
    ; and then copy them to 0x1000, 0x1100. Addition routines
loadbig_b:

add:
    clc     ; clear carry
    ; read length
    lda 0x1000
    sbc 0x1100
    bmi b_bigger
    a_bigger:
        ldx 0x1000
        jmp _done
    b_bigger:
        ldx 0x1100
    _done:
    stx 0x1200
    ldy #$1 ; 1 because first byte is size
    add_loop:
        ; X and Y are the offsets
        lda 0x1000,Y
        bcc _carry ; Branch on Carry Clear
        carry:
            clc
            adc 1 ; may set overflow
        _carry:        
        adc 0x1100,Y ; may set overflow flag
        sta 0x1200,Y
        iny
        dex
        bne add_loop
    bcc _no_carry
    
    ; final carry
    ldx 0x1200
    inx
    stx 0x1200
    lda #$1
    sta 0x1200,Y
    _no_carry:
    rts
    
message:
    .byte {{ "HELLO WORLD!" | screencode }},0
