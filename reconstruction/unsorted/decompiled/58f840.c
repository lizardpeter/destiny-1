
void FUN_0058f840(long param_1)

{
  long *plVar1;
  char cVar2;
  long lVar3;
  undefined8 uVar4;
  byte bVar5;
  long local_38;
  long local_30;
  
  plVar1 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  FUN_0058f9b0();
  if (*(char *)(param_1 + 0x114) == '\0') {
    lVar3 = FUN_005753c0(4);
    if (lVar3 != 0) {
      FUN_0058fa80(param_1,lVar3);
    }
  }
  if (*(char *)(param_1 + 0x4580) != '\0') {
    lVar3 = FUN_005753c0(4);
    if (lVar3 != 0) {
      bVar5 = *(byte *)(param_1 + 0x4580);
      if ((bVar5 & 2) != 0) {
        *(undefined4 *)(param_1 + 0x80) = 0;
        FUN_005513c0(lVar3,param_1 + 0x80);
        FUN_00551400(lVar3,param_1 + 0x80);
        cVar2 = FUN_0054e9a0(lVar3,*(undefined2 *)(param_1 + 0x42e4),
                             *(undefined2 *)(param_1 + 0x42e6),*(undefined2 *)(param_1 + 0x42ec),
                             *(undefined2 *)(param_1 + 0x42ee),param_1 + 0x104);
        if (cVar2 == '\0') {
          bVar5 = *(byte *)(param_1 + 0x4580) | 2;
        }
        else {
          bVar5 = *(byte *)(param_1 + 0x4580) & 0xfd;
        }
        *(byte *)(param_1 + 0x4580) = bVar5;
      }
      if ((bVar5 & 0x18) != 0) {
        FUN_0058fb70(param_1,lVar3);
      }
      if ((*(char *)(param_1 + 0x4581) != '\0') && ((*(byte *)(param_1 + 0x4580) & 1) != 0)) {
        FUN_0058fd40(param_1,lVar3);
      }
    }
  }
  *(char *)(param_1 + 0x4582) = *(char *)(param_1 + 0x4582) + '\x01';
  local_38 = FUN_00587580();
  if (local_38 != 0) {
    uVar4 = FUN_0056b260();
    FUN_0056bf90(uVar4,4,&local_38,param_1 + 0x4378);
  }
  if (*plVar1 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

