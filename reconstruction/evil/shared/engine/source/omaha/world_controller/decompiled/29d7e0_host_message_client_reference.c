
undefined8 FUN_0029d7e0(undefined8 param_1,undefined8 param_2)

{
  int iVar1;
  long lVar2;
  char cVar3;
  ulong uVar4;
  undefined8 uVar5;
  long lVar6;
  long lVar7;
  undefined4 local_2878 [2];
  undefined8 local_2870;
  undefined4 local_2868 [2];
  undefined8 local_2860;
  uint local_2858 [2];
  long local_2850;
  undefined4 local_283c;
  undefined4 local_2838 [2];
  undefined4 local_2830 [2];
  undefined1 local_2828 [10248];
  long local_20;
  
  local_20 = *DAT_01a1f100;
  local_2830[0] = 0x811c9dc5;
  local_283c = 0x2800;
  cVar3 = FUN_002d2b20(param_2,local_2830,local_2828,&local_283c,local_2838);
  if (cVar3 != '\0') {
    cVar3 = FUN_001071d0(local_2830,0,local_2858);
    if (cVar3 != '\0') {
      lVar6 = (ulong)(((uint)((int)local_2858[0] >> 0xd) >> 0x12 | 0x3ff) &
                     (int)local_2858[0] >> 0xd) * 0x40;
      lVar7 = *DAT_01a238a0;
      lVar2 = *(long *)(lVar7 + 0x10 + lVar6);
      uVar4 = (ulong)((local_2858[0] & 0x1fff) * *(int *)(lVar7 + 0x30 + lVar6));
      lVar7 = (lVar2 + uVar4) -
              ((long)*(int *)(lVar7 + 0x34 + lVar6) & *(ulong *)(lVar2 + 8 + uVar4));
      iVar1 = *(int *)(local_2850 + 0x108 + lVar7);
      if (((iVar1 != 0) && (iVar1 != -1)) && (*(int *)(local_2850 + 0x110 + lVar7) != -1)) {
        cVar3 = FUN_00001f70(local_2830);
        if (cVar3 != '\0') {
          FUN_001d3320(local_2868,local_2838[0],local_2828);
          local_2870 = local_2860;
          local_2878[0] = local_2868[0];
          FUN_00353340(local_2850 + 0x108 + lVar7,local_2878);
        }
        FUN_000f8210();
      }
    }
  }
  if (*DAT_01a1f100 == local_20) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),1);
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

