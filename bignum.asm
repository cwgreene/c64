    processor 6502         ; Specify the 6502 processor type
    org $0801              ; Program starting address (C64 BASIC start)

    ; C64 BASIC Program Header
    byte $0C,$08,$40,$00,$9E,$20,$32,$30,$36,$32,$00,$00,$00
    jsr $E544
    ldx #$00

    ; Set up screen memory location and text
    ldx #0                 ; Start index at 0
    jmp add

; @func copy_bignum
; Input:
;  0x60 *src
;  0x62 *dst
copy_bignum:
    ldy #$0
    lda ($60),Y
    tax
    ; store length in dest
    sta ($62),Y
    iny

    copy_bignum_loop:
        lda ($60),Y
        sta ($62),Y
        iny
        dex
        bne copy_bignum_loop
    copy_bignum_end:
    rts

; we're going to use 0x1000 for a,b,c
loadbig_a:
    ; TODO: use X to select page, Y to select offset in page
    ; and then copy them to 0x1000, 0x1100. Addition routines
loadbig_b:

; @func is_zero
; Input:
; 0x40 *a
is_zero:
    ; get length
    ldy #$0
    lda ($40),Y

    ; store length
    tax
    iny ; increment offset
    .is_zero_loop:
        lda ($40),Y
        ora #$0 ; not zero resets zero flag
        bne .ret ; return if not zero
        iny
        dex ; will set zero flag if we reach end
        bne .is_zero_loop
    .ret:
    rts

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
;    a   = 0x30 <- a
;    rem = 0x32 <- b
;    dbl = 0x30 <- a
;    acc = 0x34 -> c

    ; set up is_zero to point to remainder
    lda $0032
    sta $0040
    lda $0033
    sta $0041

    .mul_loop:
        jsr is_zero
        beq mul_end
        ; check if rem is even
        ldy #$1
        lda #$1
        and (0x32),Y
        bne .odd
        .even:
            ; dbl += dbl
            ; $30 -> #10
            ; jsr add dbl dbl -> dbl
            lda $30 ; dbl
            ldx $31
            sta $10 ; add.1 <- dbl
            stx $11

            lda $30 ; dbl
            ldx $31
            sta $12 ; add.2 <- dbl
            stx $13

            sta $14 ; add.3 <- dbl
            stx $15

            jsr add
            ; rem >> 1
            lda $32 ; rem
            ldx $33
            sta $20 ; lsr.1 <- rem
            stx $21
            jsr long_shift_right
            jmp .mul_loop
        .odd:
            ; acc += dbl
            ;jsr add (acc dbl) -> acc
            lda $34 ; acc
            ldx $35
            sta $10 ; add.1 <- acc
            stx $11
            sta $14 ; add.out <- acc
            stx $15
            lda $30 ; dbl
            ldx $31
            sta $12 ; add.2 <- dbl
            stx $13
            jsr add
            
            ; rem -= 1 (remember, we're odd)
            lda #$fe ; all ones except one bit
            ldy #$1  ; lowest order byte
                     ; note, since we're odd, this is valid. Even is handled above.
            and (0x32),Y
            sta (0x32),Y
        jmp .mul_loop
mul_end:
    rts
