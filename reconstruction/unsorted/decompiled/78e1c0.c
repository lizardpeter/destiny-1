
undefined8 FUN_0078e1c0(void)

{
  char cVar1;
  undefined4 uVar2;
  undefined8 uVar3;
  long lVar4;
  bool bVar5;
  long local_38;
  long local_30 [3];
  
  local_30[2] = *DAT_01a1f100;
  cVar1 = FUN_00752150(3);
  bVar5 = true;
  if (cVar1 != '\0') {
    cVar1 = FUN_005428c0();
    if (cVar1 != '\0') {
      uVar3 = FUN_00557c40(&DAT_026bc508);
      local_30[0] = FUN_005863c0(uVar3);
      local_30[1] = 0;
      if (local_30[0] != 0) {
        local_38 = FUN_005864b0(uVar3,local_30);
        if (local_38 != 0) {
          uVar3 = FUN_0056b260();
          if (local_38 != 0) {
            uVar2 = FUN_00001df0(uVar3);
            lVar4 = FUN_0056dc00(uVar3,3,uVar2,&local_38);
            if (lVar4 != 0) {
              bVar5 = *(int *)(lVar4 + 8) == 0;
            }
          }
        }
        goto LAB_0078e277;
      }
    }
    local_38 = 0;
  }
LAB_0078e277:
  if (*DAT_01a1f100 == local_30[2]) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),bVar5);
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

