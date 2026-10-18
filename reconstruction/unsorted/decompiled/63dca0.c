
void FUN_0063dca0(long param_1)

{
  ulong uVar1;
  long lVar2;
  undefined4 uVar3;
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
  undefined4 local_38;
  undefined4 local_34;
  long local_30;
  
  local_30 = *DAT_01a1f100;
  lVar2 = 0;
  do {
    uVar3 = 0xffffffff;
    if (*(uint *)(param_1 + 4) != 0xffffffff) {
      uVar1 = (ulong)((*(uint *)(param_1 + 4) & 0x1fff) * DAT_02689800);
      uVar3 = *(undefined4 *)
               (((DAT_026897f8 + uVar1) -
                ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar1))) + 0x2c);
    }
    FUN_0063e9d0(param_1 + 8 + lVar2,uVar3);
    lVar2 = lVar2 + 8;
  } while ((int)lVar2 != 0x40);
  if ((*(char *)(param_1 + 0xf1) != '\0') && (*(char *)(param_1 + 0xf2) == '\0')) {
    local_68 = 0;
    local_64 = 0x811c9dc5;
    local_60 = 0x811c9dc5;
    local_5c = 0x811c9dc5;
    local_58 = 0x811c9dc5;
    local_54 = 0x811c9dc5;
    lVar2 = param_1 + 0xe8;
    local_50 = 0x811c9dc5;
    local_40 = 0x811c9dc5;
    local_3c = 0x811c9dc5;
    local_38 = 0x811c9dc5;
    local_34 = 0x811c9dc5;
    local_4c = 1;
    local_48 = DAT_026bea58;
    local_44 = DAT_026bea5c;
    FUN_00320ee0(lVar2,&local_68);
    local_44 = DAT_026bea60;
    FUN_00320e60(lVar2,&local_68);
    FUN_00320f60(lVar2);
    *(undefined1 *)(param_1 + 0xf2) = 1;
  }
  *(undefined1 *)(param_1 + 0xf0) = 0;
  if (*DAT_01a1f100 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

