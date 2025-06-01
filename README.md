# event---2025-grey-cat-the-flag

    while ((local_14 != 7 &&
           ((board[(long)(local_14 + 1) * 8 + (long)iVar2] == player1symbol ||
            (board[(long)(local_14 + 1) * 8 + (long)iVar2] == player2symbol))))) {
      board[(long)iVar2 + (long)local_14 * 8] = board[(long)(local_14 + 1) * 8 + (long)iVar2];
      local_14 = local_14 + 1;
    }
    board[(long)iVar2 + (long)local_14 * 8] = local_16;