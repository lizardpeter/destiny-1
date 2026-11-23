
undefined8
FUN_0056a0c0(undefined8 param_1,undefined8 param_2,int param_3,undefined8 param_4,int *param_5,
            uint *param_6)

{
  undefined4 uVar1;
  uint uVar2;
  char cVar3;
  int iVar4;
  undefined8 uVar5;
  uint *puVar6;
  uint *puVar7;
  char cVar8;
  uint uVar9;
  int iVar10;
  undefined1 local_168 [320];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  thunk_FUN_012aa7c6(param_6,param_2,(long)param_3);
  *param_5 = param_3;
  uVar2 = *param_6;
  uVar9 = swap_bytes(uVar2);
  *param_6 = uVar9;
  if (uVar2 == 0) {
    cVar3 = FUN_000e4d70(7,4);
    cVar8 = '\0';
    if (cVar3 != '\0') {
      if ((DAT_026bac50 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026bac50), iVar4 != 0)) {
        DAT_026bac48 = FUN_000e4a10(s_networking_investment_push_queue_0163b555);
        thunk_FUN_012aa7e6(&DAT_026bac50);
      }
      cVar8 = '\0';
      FUN_01008290(local_168,s_networking_investment_push_queue_0163b555,*param_6);
      FUN_000e4aa0(DAT_026bac48,local_168);
    }
  }
  else {
    uVar9 = uVar2 >> 0x18 | (uVar2 & 0xff0000) >> 8 | (uVar2 & 0xff00) << 8 | uVar2 << 0x18;
    cVar8 = '\x01';
    puVar7 = param_6 + 1;
    for (iVar4 = 0; iVar4 < (int)uVar9; iVar4 = iVar4 + 1) {
      uVar9 = swap_bytes(*puVar7);
      *puVar7 = uVar9;
      uVar5 = swap_bytes(*(undefined8 *)(puVar7 + 1));
      *(undefined8 *)(puVar7 + 1) = uVar5;
      uVar2 = puVar7[3];
      uVar9 = swap_bytes(uVar2);
      puVar7[3] = uVar9;
      puVar6 = (uint *)((long)puVar7 + 0x15);
      uVar9 = *(uint *)((long)puVar7 + 0x11);
      uVar1 = swap_bytes(uVar9);
      *(undefined4 *)((long)puVar7 + 0x11) = uVar1;
      if (uVar2 == 0xffffffff) {
        if (uVar9 != 0) {
          cVar8 = '\0';
        }
      }
      else if (uVar9 != 0) {
        uVar9 = uVar9 >> 0x18 | (uVar9 & 0xff0000) >> 8 | (uVar9 & 0xff00) << 8 | uVar9 << 0x18;
        iVar10 = -1;
        if (cVar8 == '\0') {
          if (0 < (int)uVar9) {
            uVar1 = swap_bytes(*(undefined4 *)((long)puVar7 + 0x15));
            *(undefined4 *)((long)puVar7 + 0x15) = uVar1;
            uVar5 = swap_bytes(*(undefined8 *)((long)puVar7 + 0x19));
            *(undefined8 *)((long)puVar7 + 0x19) = uVar5;
            uVar9 = *(uint *)((long)puVar7 + 0x21);
            uVar1 = swap_bytes(uVar9);
            *(undefined4 *)((long)puVar7 + 0x21) = uVar1;
            puVar6 = (uint *)((ulong)(uVar9 >> 0x18 | (uVar9 & 0xff0000) >> 8 |
                                      (uVar9 & 0xff00) << 8 | uVar9 << 0x18) + 0x25 + (long)puVar7);
          }
        }
        else {
          while (iVar10 = iVar10 + 1, iVar10 < (int)uVar9) {
            uVar9 = swap_bytes(*puVar6);
            *puVar6 = uVar9;
            uVar5 = swap_bytes(*(undefined8 *)(puVar6 + 1));
            *(undefined8 *)(puVar6 + 1) = uVar5;
            uVar2 = puVar6[3];
            uVar9 = swap_bytes(uVar2);
            puVar6[3] = uVar9;
            puVar6 = (uint *)((ulong)(uVar2 >> 0x18 | (uVar2 & 0xff0000) >> 8 |
                                      (uVar2 & 0xff00) << 8 | uVar2 << 0x18) + 0x10 + (long)puVar6);
            uVar9 = *(uint *)((long)puVar7 + 0x11);
          }
        }
      }
      if (cVar8 == '\0') break;
      uVar9 = *param_6;
      puVar7 = puVar6;
    }
  }
  if (*DAT_01a1f100 != local_28) {
    uVar5 = thunk_FUN_012aa7f6();
    return uVar5;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),cVar8);
}

