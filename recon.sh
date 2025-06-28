#!/bin/bash
# === Binary Recon All-in-One Script ===

if [ $# -ne 1 ]; then
    echo "Usage: recon {path to exe file}"
    exit 1
fi

BIN="$1"
OUTFILE="recon_$(basename $BIN).txt"

{
echo "[*] Target Binary: $BIN"
echo

file "$BIN"

echo -e "\n[+] Checksec:"
checksec --file="$BIN"

echo -e "\n[+] ELF Header:"
readelf -h "$BIN"

echo -e "\n[+] Section Headers:"
readelf -S "$BIN"

echo -e "\n[+] Program Headers:"
readelf -l "$BIN"

echo -e "\n[+] Symbol Table:"
readelf -s "$BIN"

echo -e "\n[+] Relocations:"
readelf -r "$BIN"

echo -e "\n[+] Static Symbols:"
nm "$BIN"

echo -e "\n[+] Dynamic Symbols:"
nm -D "$BIN"

echo -e "\n[+] Strings (length ≥ 5):"
strings -n 5 "$BIN"

echo -e "\n[+] Strings with '/bin':"
strings "$BIN" | grep '/bin'

echo -e "\n[+] Disassembly (.text, Intel syntax):"
objdump -M intel -d "$BIN"

echo -e "\n[+] Hexdump of .text section:"
objdump -s -j .text "$BIN"

echo -e "\n[+] ROP Gadgets:"
ROPgadget --binary "$BIN"

echo -e "\n[+] ROP Pop/Ret Gadgets:"
ROPgadget --binary "$BIN" --only "pop|ret"

echo -e "\n[+] Syscall Gadgets:"
ROPgadget --binary "$BIN" --only "syscall"

} | tee "$OUTFILE"
