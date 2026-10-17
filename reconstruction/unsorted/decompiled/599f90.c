
void FUN_00599f90(long param_1)

{
  undefined1 uVar1;
  char cVar2;
  int iVar3;
  undefined8 uVar4;
  undefined4 *puVar5;
  int iVar6;
  short *psVar7;
  short local_1c8 [2];
  undefined4 local_1c4;
  undefined4 uStack_1c0;
  undefined4 uStack_1bc;
  undefined4 local_1b8;
  undefined4 uStack_1b4;
  int local_1b0;
  undefined1 uStack_1ac;
  undefined3 uStack_1ab;
  undefined1 local_1a8 [12];
  undefined4 local_19c;
  undefined4 local_194;
  undefined4 local_18c;
  undefined4 local_188;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  psVar7 = (short *)(param_1 + 0x458);
  iVar6 = 0;
  do {
    uVar1 = *(undefined1 *)(param_1 + 0x30);
    iVar3 = FUN_007850a0();
    local_1c8[0] = FUN_007773c0(0);
    uStack_1c0 = CONCAT31(uStack_1c0._1_3_,iVar3 == 0x24);
    uVar4 = FUN_0076a910();
    local_1b8 = (undefined4)uVar4;
    uStack_1b4 = (undefined4)((ulong)uVar4 >> 0x20);
    local_1b0 = FUN_0078c240();
    _uStack_1ac = CONCAT31(uStack_1ab,uVar1);
    FUN_000a0760(&local_1c4);
    if (local_1c8[0] != -1) {
      puVar5 = (undefined4 *)FUN_0077b9e0();
      if (iVar6 == 2) {
        local_1c4 = puVar5[0x28];
      }
      else if (iVar6 == 1) {
        local_1c4 = *puVar5;
      }
    }
    if (((((local_1c8[0] != *psVar7) || (cVar2 = FUN_000f93a0(&local_1c4,psVar7 + 2), cVar2 == '\0')
          ) || ((char)uStack_1c0 != (char)psVar7[4])) ||
        ((CONCAT44(uStack_1b4,local_1b8) != *(long *)(psVar7 + 8) ||
         (local_1b0 != *(int *)(psVar7 + 0xc))))) || ((char)_uStack_1ac != (char)psVar7[0xe])) {
      if (local_1c8[0] == -1) {
        *psVar7 = -1;
        FUN_000a0760(psVar7 + 2);
        *(undefined1 *)(psVar7 + 4) = 0;
        psVar7[8] = 0;
        psVar7[9] = 0;
        psVar7[10] = 0;
        psVar7[0xb] = 0;
        psVar7[0xc] = 0;
        psVar7[0xd] = 0;
        *(undefined1 *)(psVar7 + 0xe) = 0;
        FUN_00b0dcb0();
        psVar7[200] = 0;
        psVar7[0xc9] = 0;
      }
      else {
        local_19c = 0x811c9dc5;
        local_194 = 0x811c9dc5;
        local_18c = 0x811c9dc5;
        local_188 = 0x811c9dc5;
        if ((iVar6 == 2) || (iVar6 == 1)) {
          FUN_0059a500(param_1,local_1c8,local_1a8);
        }
        else if (iVar6 == 0) {
          FUN_0059a210(param_1,local_1c8,local_1a8);
        }
        iVar3 = thunk_FUN_012aa826(local_1a8,psVar7 + 0x10,0x170);
        if (iVar3 != 0) {
          thunk_FUN_012aa7c6(psVar7 + 0x10,local_1a8,0x170);
          iVar3 = *(int *)(psVar7 + 200) + 1;
          if (iVar3 == 0) {
            iVar3 = 1;
          }
          *(int *)(psVar7 + 200) = iVar3;
        }
      }
      *psVar7 = local_1c8[0];
      *(undefined1 *)(psVar7 + 0xe) = uStack_1ac;
      *(ulong *)(psVar7 + 10) = CONCAT44(local_1b0,uStack_1b4);
      *(ulong *)(psVar7 + 6) = CONCAT44(local_1b8,uStack_1bc);
      *(ulong *)(psVar7 + 2) = CONCAT44(uStack_1c0,local_1c4);
    }
    psVar7 = psVar7 + 0xcc;
    iVar6 = iVar6 + 1;
  } while (iVar6 != 3);
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

