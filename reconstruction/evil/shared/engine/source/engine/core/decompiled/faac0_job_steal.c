
bool FUN_000faac0(void)

{
  byte bVar1;
  char cVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  long lVar6;
  int iVar7;
  ulong uVar8;
  ulong uVar9;
  int iVar10;
  undefined8 local_58;
  ushort local_4a;
  undefined8 local_48;
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar4 = FUN_000fc4e0();
  lVar6 = FUN_000fc520();
  local_58 = 0xffffffffffffffff;
  uVar9 = *(ulong *)(lVar6 + 8);
  if ((9 < (byte)uVar9) || (uVar8 = 0, (0x2aaUL >> (uVar9 & 0x3f) & 1) == 0)) {
    local_58 = CONCAT71(0xffffffffffffff,(byte)uVar9);
    uVar8 = 1;
  }
  bVar1 = (byte)(uVar9 >> 8);
  if ((9 < bVar1) || ((0x2aaUL >> (uVar9 >> 8 & 0x3f) & 1) == 0)) {
    *(byte *)((ulong)&local_58 | uVar8) = bVar1;
    uVar8 = (ulong)((int)uVar8 + 1);
  }
  iVar7 = (int)uVar8;
  bVar1 = (byte)(uVar9 >> 0x10);
  if ((9 < bVar1) || ((0x2aaUL >> (uVar9 >> 0x10 & 0x3f) & 1) == 0)) {
    *(byte *)((long)&local_58 + (long)iVar7) = bVar1;
    iVar7 = iVar7 + 1;
  }
  bVar1 = (byte)(uVar9 >> 0x18);
  if ((9 < bVar1) || ((0x2aaUL >> (uVar9 >> 0x18 & 0x3f) & 1) == 0)) {
    *(byte *)((long)&local_58 + (long)iVar7) = bVar1;
    iVar7 = iVar7 + 1;
  }
  bVar1 = (byte)(uVar9 >> 0x20);
  if ((9 < bVar1) || ((0x2aaUL >> (uVar9 >> 0x20 & 0x3f) & 1) == 0)) {
    *(byte *)((long)&local_58 + (long)iVar7) = bVar1;
    iVar7 = iVar7 + 1;
  }
  bVar1 = (byte)(uVar9 >> 0x28);
  if ((9 < bVar1) || ((0x2aaUL >> (uVar9 >> 0x28 & 0x3f) & 1) == 0)) {
    *(byte *)((long)&local_58 + (long)iVar7) = bVar1;
    iVar7 = iVar7 + 1;
  }
  bVar1 = (byte)(uVar9 >> 0x30);
  if ((9 < bVar1) || ((0x2aaUL >> (uVar9 >> 0x30 & 0x3f) & 1) == 0)) {
    *(byte *)((long)&local_58 + (long)iVar7) = bVar1;
    iVar7 = iVar7 + 1;
  }
  bVar1 = (byte)(uVar9 >> 0x38);
  if ((9 < bVar1) || ((0x2aaUL >> (uVar9 >> 0x38 & 0x3f) & 1) == 0)) {
    *(byte *)((long)&local_58 + (long)iVar7) = bVar1;
  }
  local_48 = local_58;
  iVar10 = 1;
  iVar7 = 0;
  do {
    local_4a = 0xffff;
    cVar2 = FUN_000fa750(DAT_025d1270 + 0x19990,&local_48,&local_4a);
    if (cVar2 == '\0') {
      if (0 < iVar7) {
        iVar10 = 0;
      }
      iVar7 = iVar7 + 1;
    }
    else {
      uVar9 = (ulong)local_4a;
      uVar5 = FUN_000fc560();
      FUN_000fc460(uVar9);
      *(undefined1 *)(DAT_025d1270 + 0x10008 + uVar9 * 0x10) = 5;
      lVar6 = DAT_025d1270;
      FUN_000fd8f0(&local_40,DAT_025d1270 + 0x10000 + uVar9 * 0x10);
      FUN_000fa980(uVar9 * 0x80 + lVar6,uVar4,local_40);
      FUN_000fc460(uVar5);
      iVar10 = iVar10 + -1;
      iVar7 = 0;
    }
  } while (iVar10 != 0);
  if (*DAT_01a1f100 == local_38) {
    return iVar7 < 2;
  }
  uVar3 = thunk_FUN_012aa7f6();
  return (bool)uVar3;
}

