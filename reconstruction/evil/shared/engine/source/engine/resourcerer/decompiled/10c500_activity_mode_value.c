
undefined8 FUN_0010c500(int *param_1)

{
  long lVar1;
  long lVar2;
  char cVar3;
  undefined8 uVar4;
  int iVar5;
  ulong uVar6;
  char *pcVar7;
  long lVar8;
  uint local_38 [2];
  long local_30;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  cVar3 = FUN_001072c0(0x10,0,local_38);
  uVar4 = 0;
  if (cVar3 != '\0') {
    if (local_38[0] != 0xffffffff) {
      lVar8 = (ulong)(((uint)((int)local_38[0] >> 0xd) >> 0x12 | 0x3ff) & (int)local_38[0] >> 0xd) *
              0x40;
      lVar1 = *DAT_01a238a0;
      lVar2 = *(long *)(lVar1 + 0x10 + lVar8);
      uVar6 = (ulong)((local_38[0] & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar8));
      pcVar7 = (char *)(((lVar2 + uVar6) -
                        ((long)*(int *)(lVar1 + 0x34 + lVar8) & *(ulong *)(lVar2 + 8 + uVar6))) +
                        local_30 + 0x1ac);
      if ((pcVar7 != (char *)0x0) && (iVar5 = (int)*pcVar7, iVar5 != -1)) {
        *param_1 = iVar5;
        uVar4 = 1;
      }
    }
  }
  if (*DAT_01a1f100 == local_20) {
    return uVar4;
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

