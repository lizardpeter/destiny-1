
void FUN_005a0690(void)

{
  char cVar1;
  int iVar2;
  undefined1 local_158 [320];
  long local_18;
  
  local_18 = *DAT_01a1f100;
  cVar1 = FUN_000e4d70(0xd,2);
  if (cVar1 != '\0') {
    if (DAT_026bd7d0 == '\0') {
      iVar2 = thunk_FUN_012aa7d6(&DAT_026bd7d0);
      if (iVar2 != 0) {
        DAT_026bd7c8 = FUN_000e4a10(s_networking_online_ownership_mana_01640f6f);
        thunk_FUN_012aa7e6(&DAT_026bd7d0);
      }
    }
    FUN_01008290(local_158,s_networking_online_ownership_mana_01640f6f);
    FUN_000e4aa0(DAT_026bd7c8,local_158);
  }
  if (DAT_026bd700 != 0) {
    FUN_0059fd30(0);
    DAT_026bd708 = 1;
  }
  if (*DAT_01a1f100 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

