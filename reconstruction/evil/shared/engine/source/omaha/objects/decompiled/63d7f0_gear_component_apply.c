
void FUN_0063d7f0(long param_1,undefined4 *param_2)

{
  undefined4 *puVar1;
  long lVar2;
  long lVar3;
  ulong uVar4;
  undefined4 uVar5;
  undefined4 local_70;
  undefined4 local_6c;
  undefined4 local_68;
  undefined4 local_64;
  undefined4 local_60;
  undefined4 local_5c;
  undefined4 local_58;
  undefined4 local_54;
  undefined4 local_50;
  undefined4 local_4c;
  undefined4 local_48;
  undefined4 local_44;
  undefined4 local_40;
  undefined4 local_3c;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar5 = 0xffffffff;
  if (*(uint *)(param_1 + 4) != 0xffffffff) {
    uVar4 = (ulong)((*(uint *)(param_1 + 4) & 0x1fff) * DAT_02689800);
    uVar5 = *(undefined4 *)
             (((DAT_026897f8 + uVar4) - ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar4)))
             + 0x2c);
  }
  lVar2 = param_1 + 0xf3;
  lVar3 = param_1 + 0xf4;
  puVar1 = param_2 + 8;
  FUN_0063ea00(param_1 + 8,uVar5,lVar2,lVar3,*param_2);
  FUN_0063ea00(param_1 + 0x10,uVar5,lVar2,lVar3,param_2[1],puVar1);
  FUN_0063ea00(param_1 + 0x18,uVar5,lVar2,lVar3,param_2[2],puVar1);
  FUN_0063ea00(param_1 + 0x20,uVar5,lVar2,lVar3,param_2[3],puVar1);
  FUN_0063ea00(param_1 + 0x28,uVar5,lVar2,lVar3,param_2[4],puVar1);
  FUN_0063ea00(param_1 + 0x30,uVar5,lVar2,lVar3,param_2[5],puVar1);
  FUN_0063ea00(param_1 + 0x38,uVar5,lVar2,lVar3,param_2[6],puVar1);
  FUN_0063ea00(param_1 + 0x40,uVar5,lVar2,lVar3,param_2[7],puVar1);
  if ((*(char *)(param_1 + 0xf1) != '\0') && (*(char *)(param_1 + 0xf2) != '\0')) {
    local_70 = 0;
    local_6c = 0x811c9dc5;
    local_68 = 0x811c9dc5;
    local_64 = 0x811c9dc5;
    local_60 = 0x811c9dc5;
    local_5c = 0x811c9dc5;
    lVar2 = param_1 + 0xe8;
    local_58 = 0x811c9dc5;
    local_48 = 0x811c9dc5;
    local_44 = 0x811c9dc5;
    local_40 = 0x811c9dc5;
    local_3c = 0x811c9dc5;
    local_54 = 1;
    local_50 = DAT_026bea58;
    local_4c = DAT_026bea60;
    FUN_00320ee0(lVar2,&local_70);
    local_4c = DAT_026bea5c;
    FUN_00320e60(lVar2,&local_70);
    FUN_00320f60(lVar2);
    *(undefined1 *)(param_1 + 0xf2) = 0;
  }
  FUN_0063e6c0(param_1);
  *(undefined1 *)(param_1 + 0xf0) = 1;
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

