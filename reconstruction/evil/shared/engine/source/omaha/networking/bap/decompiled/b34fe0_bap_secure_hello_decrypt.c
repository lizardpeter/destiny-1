
undefined1
FUN_00b34fe0(long param_1,undefined4 *param_2,ulong param_3,long *param_4,undefined4 *param_5)

{
  ulong uVar1;
  byte bVar2;
  byte bVar3;
  char cVar4;
  ulong uVar5;
  long lVar6;
  byte *pbVar7;
  undefined1 uVar8;
  undefined4 uVar9;
  long lVar10;
  int iVar11;
  
  iVar11 = swap_bytes(*param_2);
  lVar10 = (long)iVar11;
  uVar8 = 0;
  uVar9 = 5;
  lVar6 = 0;
  if (lVar10 + 4U <= param_3) {
    cVar4 = FUN_0006d4d0(param_1 + 0x20,param_2,lVar10 + -0x1c,(long)param_2 + lVar10 + -0x1c);
    uVar9 = 1;
    if (cVar4 != '\0') {
      uVar1 = lVar10 - 0x30;
      cVar4 = FUN_0006c620(param_1,param_2 + 5,uVar1,param_2 + 1,param_2,uVar1);
      uVar9 = 4;
      if (cVar4 != '\0') {
        bVar2 = *(byte *)(lVar10 + -0x31 + (long)param_2);
        uVar5 = (ulong)bVar2;
        uVar9 = 3;
        if (((uVar5 != 0) && (bVar2 < 0x11)) && (uVar5 <= uVar1)) {
          lVar6 = uVar1 - uVar5;
          iVar11 = (iVar11 + -0x30) - (uint)bVar2;
          pbVar7 = (byte *)((long)iVar11 + (long)param_2);
          do {
            if ((int)uVar1 <= iVar11) {
              uVar9 = 0;
              uVar8 = 1;
              goto LAB_00b350cb;
            }
            iVar11 = iVar11 + 1;
            bVar3 = *pbVar7;
            pbVar7 = pbVar7 + 1;
          } while (bVar3 == bVar2);
          uVar9 = 3;
        }
      }
    }
    thunk_FUN_012aa986(param_2,0,param_3);
    uVar8 = 0;
    lVar6 = 0;
  }
LAB_00b350cb:
  *param_5 = uVar9;
  *param_4 = lVar6;
  return uVar8;
}

