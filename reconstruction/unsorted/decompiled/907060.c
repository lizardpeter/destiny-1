
void FUN_00907060(void)

{
  undefined4 uVar1;
  
  if ((&DAT_00002b50)[DAT_0273dcd0] == '\0') {
    (&DAT_00002b50)[DAT_0273dcd0] = 1;
    (&DAT_00002b51)[DAT_0273dcd0] = 0;
    uVar1 = FUN_00591c80(DAT_0166b270);
    *(undefined4 *)(&DAT_00002b54 + DAT_0273dcd0) = uVar1;
    (&DAT_00002b59)[DAT_0273dcd0] = 0;
  }
  return;
}

