
void FUN_0056bd50(long param_1,undefined4 param_2,long *param_3)

{
  int iVar1;
  long lVar2;
  char *pcVar3;
  long lVar4;
  undefined8 *puVar5;
  long lVar6;
  uint uVar7;
  ulong uVar8;
  
  lVar2 = 0x60;
  pcVar3 = (char *)0x0;
  while ((*(char *)(param_1 + lVar2) != (char)param_2 ||
         (*(long *)(param_1 + 0x20 + lVar2) != *param_3))) {
    lVar2 = lVar2 + 0x40;
    if ((int)lVar2 == 0x40a0) {
LAB_0056bd95:
      iVar1 = FUN_00280b70(param_2);
      if (iVar1 == 1) {
        FUN_00552b10((int)*pcVar3,pcVar3 + 0x20);
      }
      lVar2 = 0;
      do {
        if (0 < *(short *)(pcVar3 + lVar2 * 4 + 4)) {
          lVar4 = (long)*pcVar3 * 0x60 + param_1;
          lVar6 = (long)*(int *)(lVar2 * 0x10 + 0x4fd98 + lVar4);
          uVar8 = (ulong)*(uint *)(lVar2 * 0x10 + 0x4fd90 + lVar4);
          lVar4 = 0;
          if (uVar8 != 0xffffffff) {
            lVar4 = uVar8 + param_1 + 0x40a0;
          }
          uVar8 = (ulong)*(short *)(pcVar3 + lVar2 * 4 + 2);
          puVar5 = (undefined8 *)(uVar8 * lVar6 + lVar4);
          do {
            thunk_FUN_012aa986(puVar5,0,lVar6);
            *puVar5 = 0;
            puVar5 = (undefined8 *)((long)puVar5 + lVar6);
            uVar7 = (int)uVar8 + 1;
            uVar8 = (ulong)uVar7;
          } while ((int)uVar7 <
                   (int)*(short *)(pcVar3 + lVar2 * 4 + 4) + (int)*(short *)(pcVar3 + lVar2 * 4 + 2)
                  );
        }
        lVar2 = lVar2 + 1;
      } while ((int)lVar2 != 6);
      pcVar3[0x20] = '\0';
      pcVar3[0x21] = '\0';
      pcVar3[0x22] = '\0';
      pcVar3[0x23] = '\0';
      pcVar3[0x24] = '\0';
      pcVar3[0x25] = '\0';
      pcVar3[0x26] = '\0';
      pcVar3[0x27] = '\0';
      pcVar3[0x28] = '\0';
      pcVar3[0x29] = '\0';
      pcVar3[0x3c] = -1;
      pcVar3[0x3d] = -1;
      pcVar3[0x3e] = -1;
      pcVar3[0x3f] = -1;
      FUN_00543ee0(pcVar3 + 0x2c);
      FUN_00543ee0(pcVar3 + 0x34);
      return;
    }
  }
  pcVar3 = (char *)(lVar2 + param_1);
  goto LAB_0056bd95;
}

