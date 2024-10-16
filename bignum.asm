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

; @func long_shift_right
; Input:
;  0x20 *a
; Output:
;  0x20 *a
long_shift_right:
    ldy #$0
    ; get length
    lda ($20),Y
    tax
    iny

    ; initial shift
    lda ($20), Y
    lsr A

    iny
    dex
    beq lsr_end
    lsr_loop:
        lda ($20),Y
        lsr A
        bcc lsr_next
        lsr_increment_carry:
            dey
            lda ($20),Y
            ORA 0x80
            iny
        lsr_next:
        iny
        dex
        bne loop
    lsr_end:
    rts

; @func add
; Input:
;  0x10 *a
;  0x12 *b
; Output:
;  0x14 *c
add:
    clc     ; clear carry
    ; read length
    ldy #$0
    lda ($10),Y
    sbc ($12),Y
    bmi b_bigger
    a_bigger:
        lda ($10),Y
        tax
        jmp _done
    b_bigger:
        lda ($12),Y
        tax
    _done:
    sta ($14),Y
    tay
    ldy #$1 ; 1 because first byte is size
    add_loop:
        ; X and Y are the offsets
        lda ($10),Y
        adc ($12),Y ; may set carry flag
        sta ($14),Y
        iny
        dex
        bne add_loop
    bcc _no_carry
    
    ; final carry
    clc
    ; attach 1 to end
    lda #$1
    sta ($14),Y

    ; increment length
    ldy #$0
    lda ($14),Y
    adc #$1
    sta ($14),Y
    _no_carry:
add_end:
    rts

;mul:
;   clc
;   dbl = 0x1300 <- a
;   rem = 0x1400 <- b
;   acc = 0x1500
;   mul_loop:
;       lda 0x1
;       and 0x1400
;       bcc odd
;       even:
;           jsr long_shift_left 0x1400
;           jsr long_shift_right 0x1300
;       odd:
;           jsr add acc dbl
;           jsr copy result -> acc; needed?
;           lda #$1
;           and 0x1401
;           sta somewhere?
;       bne mul_loop

message:
    .byte {{ "HELLO WORLD!" | screencode }},0
