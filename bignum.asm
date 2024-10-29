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
    lda ($20),Y
    lsr
    sta ($20),Y

    iny
    dex
    beq lsr_end
    lsr_loop:
        lda ($20),Y
        lsr
        sta ($20),Y
        bcc lsr_next
        lsr_increment_carry:
            dey
            lda ($20),Y
            ORA 0x80
            sta ($20),Y
            iny
        lsr_next:
        iny
        dex
        bne lsr_loop
    lsr_end:
    long_shift_right_end:
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
    bmi add_b_bigger
    add_a_bigger:
        lda ($10),Y
        tax
        jmp add_done
    add_b_bigger:
        lda ($12),Y
        tax
    add_done:
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
    bcc add_no_carry
    
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
    add_no_carry:
add_end:
    rts

; @func mul
; Input:
;  0x30 *a - destructive!
;  0x32 *b - destructive!
; Output:
;  0x34 *c
mul:
    clc
;    dbl = 0x30 <- a
;    rem = 0x32 <- b
;    acc = 0x34 -> c
    .mul_loop:
        ; check if rem is even
        ldy #$1
        lda #$1
        and (0x32),Y
        bcc .odd
        .even:
            ; dbl += dbl
            ; $30 -> #10
            ; jsr add acc acc -> acc
            lda $30 ; acc
            ldx $31
            sta $10 ; add.1 <- acc
            stx $11

            sta $12 ; add.2 <- acc
            stx $13

            sta $14 ; add.3 <- acc
            stx $15

            jsr add
            ; rem >> 1
            lda $32 ; rem
            ldx $33
            sta $20 ; lsr.1 <- rem
            stx $21
            jsr long_shift_right
        .odd:
            ; acc += dbl
            ;jsr add (acc dbl) -> acc
            lda $30 ; acc
            ldx $31
            sta $10 ; add.1 <- acc
            stx $11
            sta $14 ; add.out <- acc
            stx $15
            lda $32 ; dbl
            ldx $33
            sta $12 ; add.2 <- dbl
            stx $13
            
            ; rem -= 1
            lda #$1
            ldy #$1
            and (0x32),Y
            sta (0x32),Y
        bne mul_loop
mul_end:
    rts
