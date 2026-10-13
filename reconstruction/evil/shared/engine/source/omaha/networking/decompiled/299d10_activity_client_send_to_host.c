
bool FUN_00299d10(long param_1,undefined8 param_2,ulong param_3,undefined4 param_4,
                 undefined8 param_5,undefined4 param_6,byte *param_7)

{
  char cVar1;
  char cVar2;
  undefined1 uVar3;
  undefined8 uVar4;
  undefined4 local_4c;
  undefined1 local_48 [8];
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if ((*param_7 & 1) == 0) {
    FUN_000b54b0(local_48,0x1df00,0x19,s_activity_client_send_message_01622d33);
    local_4c = 0;
    cVar2 = FUN_002a4b70(param_4,param_5,local_40,&local_4c);
    cVar1 = '\0';
    if (cVar2 != '\0') {
      cVar1 = (**(code **)(**(long **)(param_1 + 0xe50) + 0x30))
                        (*(long **)(param_1 + 0xe50),param_2,param_3 & 0xffffffff,local_40,local_4c,
                         *(undefined4 *)(param_1 + 0x6c6c));
    }
    FUN_000b54e0(local_48);
  }
  else {
    cVar1 = (**(code **)(**(long **)(param_1 + 0xe50) + 0x30))
                      (*(long **)(param_1 + 0xe50),param_2,param_3,param_5,param_6,
                       *(undefined4 *)(param_1 + 0x6c6c));
  }
  if (cVar1 != '\0') {
    uVar4 = DAT_026553b0;
    if (DAT_026553a8 == '\0') {
      uVar4 = FUN_000694d0();
    }
    *(undefined8 *)(param_1 + 0xe48) = uVar4;
  }
  if (*DAT_01a1f100 != local_38) {
    uVar3 = thunk_FUN_012aa7f6();
    return (bool)uVar3;
  }
  return cVar1 != '\0';
}

