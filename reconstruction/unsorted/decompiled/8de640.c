
void FUN_008de640(undefined4 param_1,long param_2,undefined4 param_3,undefined4 *param_4)

{
  char cVar1;
  undefined4 uVar2;
  ulong uVar3;
  long lVar4;
  int iVar5;
  float fVar6;
  undefined1 local_61;
  int local_60;
  int local_5c;
  undefined8 local_58;
  undefined4 local_50;
  undefined8 local_4c;
  undefined4 local_44;
  char local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar3 = FUN_0093e280();
  local_61 = 0;
  if ((uVar3 & 1) == 0) {
    cVar1 = '\0';
  }
  else {
    cVar1 = FUN_0093e2a0(0,&local_60);
    if (cVar1 == '\0') {
      cVar1 = '\0';
    }
    else if (local_60 == 0) {
      cVar1 = '\0';
    }
    else {
      iVar5 = -1;
      if (local_5c != -1) {
        lVar4 = FUN_00074a30(DAT_0273ea80);
        if ((lVar4 != 0) && ((*(byte *)(lVar4 + 0x610) & 2) == 0)) {
          uVar2 = FUN_00917a40(local_5c);
          FUN_00923430(param_3,uVar2);
          iVar5 = *(int *)(lVar4 + 0x644);
        }
      }
      if (local_60 == 2) {
        FUN_008dedc0(param_2,iVar5);
        *(undefined4 *)(param_2 + 200) = local_50;
        *(undefined8 *)(param_2 + 0xc0) = local_58;
        *(undefined4 *)(param_2 + 0xd4) = local_44;
        *(undefined8 *)(param_2 + 0xcc) = local_4c;
        param_4[3] = local_50;
        *(undefined8 *)(param_4 + 1) = local_58;
        param_4[0x11] = *(undefined4 *)(param_2 + 0xd4);
        *(undefined8 *)(param_4 + 0xf) = *(undefined8 *)(param_2 + 0xcc);
        FUN_000a8ad0(param_4 + 0xf,param_4 + 0x12);
        if (local_40 == '\0') {
          fVar6 = (float)thunk_FUN_00526fe0();
        }
        else {
          fVar6 = (float)FUN_00527470();
          fVar6 = fVar6 * DAT_01669db0;
        }
        param_4[0xc] = fVar6;
        cVar1 = *(char *)(param_2 + 0x55);
        if (*(char *)(param_2 + 0x55) != local_40) {
          uVar2 = FUN_00527550();
          param_4[0x4f] = uVar2;
          *(undefined1 *)((long)param_4 + 0x121) = 1;
          cVar1 = local_40;
        }
        param_4[0x2c] = *(undefined4 *)(&DAT_01669db4 + (ulong)(iVar5 == -1) * 4);
        *param_4 = 0x8001;
      }
      else if (local_60 == 1) {
        uVar2 = FUN_006ed8f0(iVar5);
        FUN_008e77e0(param_2 + 0x58,uVar2);
        FUN_008e6980(param_1,param_2 + 0x58,param_3,param_4);
        local_61 = 1;
        cVar1 = '\0';
      }
      else {
        cVar1 = '\0';
      }
    }
  }
  *(undefined1 *)(param_2 + 0x54) = local_61;
  *(char *)(param_2 + 0x55) = cVar1;
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

