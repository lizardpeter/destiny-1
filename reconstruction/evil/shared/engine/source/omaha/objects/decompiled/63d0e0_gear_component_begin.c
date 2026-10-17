
void FUN_0063d0e0(char *param_1,undefined8 param_2,undefined8 param_3)

{
  char *pcVar1;
  char cVar2;
  ulong uVar3;
  uint uVar4;
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
  FUN_001d3770(param_1 + 0xb8);
  uVar4 = 0x1fff;
  if (*(uint *)(param_1 + 4) != 0xffffffff) {
    uVar3 = (ulong)((*(uint *)(param_1 + 4) & 0x1fff) * DAT_02689800);
    uVar4 = *(uint *)(((DAT_026897f8 + uVar3) -
                      ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar3))) + 0x2c) & 0x1fff;
  }
  FUN_00337fe0((ulong)(uVar4 * DAT_02692230) + DAT_02692228,*(undefined4 *)PTR_DAT_0198e9d0,
               param_1 + 0xb8,0);
  cVar2 = FUN_0063b470(param_3);
  if (cVar2 == '\0') {
    FUN_0063d290(param_1,2,param_2,param_3);
    if (*param_1 != '\x02') {
      if ((param_1[0xf1] != '\0') && (param_1[0xf2] == '\0')) {
        local_70 = 0;
        local_6c = 0x811c9dc5;
        local_68 = 0x811c9dc5;
        local_64 = 0x811c9dc5;
        local_60 = 0x811c9dc5;
        local_5c = 0x811c9dc5;
        pcVar1 = param_1 + 0xe8;
        local_58 = 0x811c9dc5;
        local_48 = 0x811c9dc5;
        local_44 = 0x811c9dc5;
        local_40 = 0x811c9dc5;
        local_3c = 0x811c9dc5;
        local_54 = 1;
        local_50 = DAT_026bea58;
        local_4c = DAT_026bea5c;
        FUN_00320ee0(pcVar1,&local_70);
        local_4c = DAT_026bea60;
        FUN_00320e60(pcVar1,&local_70);
        FUN_00320f60(pcVar1);
        param_1[0xf2] = '\x01';
      }
      goto LAB_0063d1a6;
    }
  }
  FUN_0063d7f0(param_1,param_2);
LAB_0063d1a6:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

