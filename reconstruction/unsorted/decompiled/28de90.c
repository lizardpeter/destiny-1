
bool FUN_0028de90(long param_1,undefined8 param_2,long param_3,long param_4,undefined8 param_5,
                 long param_6,undefined8 param_7,undefined8 param_8,undefined8 param_9,
                 undefined1 param_10,undefined8 param_11,undefined8 param_12,undefined8 param_13)

{
  undefined1 uVar1;
  int iVar2;
  char local_39;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_39 = '\x01';
  thunk_FUN_012aa986(param_11,0,0x6000);
  thunk_FUN_012aa986(param_12,0,0x6000);
  thunk_FUN_012aa986(param_13,0,0x6000);
  FUN_0028bc60(param_1,param_2,param_3,param_4,param_5,param_6,param_7,param_8,param_9,0xc,param_10,
               param_11,&local_39);
  FUN_0028bc60(param_1,param_2,param_3,param_4,param_5,param_6,param_7,param_8,param_9,0xb,param_10,
               param_11,&local_39);
  if ((((param_3 == 0) || (param_4 == 0)) || (param_1 == 0)) || (param_6 == 0)) {
    local_39 = '\0';
  }
  else {
    FUN_0028cbf0(param_1,param_3 + 0x4c0,param_4 + 0x30,param_4 + 0x2b80,param_6,param_7,param_9,
                 param_12,&local_39);
  }
  iVar2 = 10;
  do {
    iVar2 = iVar2 + -1;
    FUN_0028bc60(param_1,param_2,param_3,param_4,param_5,param_6,param_7,param_8,param_9,iVar2,
                 param_10,param_13,&local_39);
  } while (0 < iVar2);
  if (*DAT_01a1f100 == local_38) {
    return local_39 != '\0';
  }
  uVar1 = thunk_FUN_012aa7f6();
  return (bool)uVar1;
}

