
void FUN_0100c790(int *param_1,char param_2)

{
  int iVar1;
  
  if (param_2 == '\0') {
    LOCK();
    iVar1 = *param_1;
    if (iVar1 == 0) {
      *param_1 = 1;
      iVar1 = 0;
    }
    UNLOCK();
    if (iVar1 == 0) {
      FUN_000f4e40(param_1[8],0);
    }
    LOCK();
    iVar1 = param_1[1];
    if (iVar1 == 0) {
      param_1[1] = 1;
      iVar1 = 0;
    }
    UNLOCK();
    if (iVar1 == 0) {
      FUN_000f4e40(param_1[9],0);
    }
    LOCK();
    iVar1 = param_1[2];
    if (iVar1 == 0) {
      param_1[2] = 1;
      iVar1 = 0;
    }
    UNLOCK();
    if (iVar1 == 0) {
      FUN_000f4e40(param_1[10],0);
    }
    LOCK();
    iVar1 = param_1[3];
    if (iVar1 == 0) {
      param_1[3] = 1;
      iVar1 = 0;
    }
    UNLOCK();
    if (iVar1 == 0) {
      FUN_000f4e40(param_1[0xb],0);
    }
    LOCK();
    iVar1 = param_1[4];
    if (iVar1 == 0) {
      param_1[4] = 1;
      iVar1 = 0;
    }
    UNLOCK();
    if (iVar1 == 0) {
      FUN_000f4e40(param_1[0xc],0);
    }
    LOCK();
    iVar1 = param_1[5];
    if (iVar1 == 0) {
      param_1[5] = 1;
      iVar1 = 0;
    }
    UNLOCK();
    if (iVar1 == 0) {
      FUN_000f4e40(param_1[0xd],0);
    }
    LOCK();
    iVar1 = param_1[6];
    if (iVar1 == 0) {
      param_1[6] = 1;
      iVar1 = 0;
    }
    UNLOCK();
    if (iVar1 == 0) {
      FUN_000f4e40(param_1[0xe],0);
    }
    LOCK();
    iVar1 = param_1[7];
    if (iVar1 == 0) {
      param_1[7] = 1;
      iVar1 = 0;
    }
    UNLOCK();
    if (iVar1 != 0) {
      return;
    }
  }
  else {
    FUN_000f4e40(param_1[8],0);
    FUN_000f4e40(param_1[9],0);
    FUN_000f4e40(param_1[10],0);
    FUN_000f4e40(param_1[0xb],0);
    FUN_000f4e40(param_1[0xc],0);
    FUN_000f4e40(param_1[0xd],0);
    FUN_000f4e40(param_1[0xe],0);
  }
  FUN_000f4e40(param_1[0xf],0);
  return;
}

