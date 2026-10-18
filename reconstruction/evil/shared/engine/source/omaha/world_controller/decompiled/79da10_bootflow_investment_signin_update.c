
void FUN_0079da10(long param_1)

{
  long *plVar1;
  char cVar2;
  long lVar3;
  undefined8 uVar4;
  undefined1 local_60 [8];
  undefined4 local_58 [2];
  undefined1 local_50 [8];
  undefined4 local_48 [2];
  undefined1 local_40 [8];
  undefined4 local_38 [2];
  undefined8 local_30;
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  if (*(int *)(param_1 + 0x30) == 7) {
    if (*(int *)(param_1 + 0x34) == 3) {
      cVar2 = FUN_00244ee0(&local_30);
      if (cVar2 != '\0') {
        lVar3 = FUN_0057ddd0(local_30);
        if (lVar3 != 0) {
          local_38[0] = DAT_026dc258;
          FUN_00546b40(local_40,(int)*(char *)(lVar3 + 0x1a));
          FUN_007bc410(local_38,local_40);
          local_48[0] = DAT_026dc254;
          FUN_00546b60(local_50,(int)*(char *)(lVar3 + 0x1c));
          FUN_007bc410(local_48,local_50);
          local_58[0] = DAT_026dc250;
          FUN_00546b80(local_60,(int)*(char *)(lVar3 + 0x1d));
          FUN_007bc410(local_58,local_60);
        }
      }
      FUN_0078c310(0);
      cVar2 = FUN_0057f5e0();
      FUN_0078c370(cVar2);
      if (cVar2 == '\0') {
        uVar4 = 0x15;
      }
      else {
        uVar4 = 0x16;
      }
      FUN_00783ed0(uVar4);
    }
    else {
      FUN_0079dd90();
    }
  }
  else {
    FUN_0079db30();
  }
  if (*plVar1 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

