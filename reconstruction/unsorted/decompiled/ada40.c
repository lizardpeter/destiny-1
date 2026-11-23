
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000ada40(void)

{
  long *plVar1;
  int iVar2;
  undefined1 local_38 [4];
  uint local_34;
  char local_2e;
  byte local_2d;
  undefined1 local_2c;
  long local_18;
  
  plVar1 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  _DAT_01ad4f38 = 0;
  _DAT_01ad4f30 = 0;
  _DAT_01ad4f28 = 0;
  _DAT_01ad4f20 = 0;
  _DAT_01ad4f18 = 0;
  _DAT_01ad4f10 = 0;
  _DAT_01ad4f08 = 0;
  _DAT_01ad4f00 = 0;
  _DAT_01ad4ef8 = 0;
  _DAT_01ad4ef0 = 0;
  _DAT_01ad4ee8 = 0;
  _DAT_01ad4ee0 = 0;
  _DAT_01ad4ed8 = 0;
  thunk_FUN_012aae06();
  iVar2 = thunk_FUN_012aac46(&DAT_01ad4f3c);
  if (iVar2 == -0x7f69fffe) {
    thunk_FUN_012aac56(0);
    iVar2 = thunk_FUN_012aac46(&DAT_01ad4f3c);
  }
  if (iVar2 == 0) {
    if (DAT_01ad4f3c != 0) {
      iVar2 = thunk_FUN_012aae16(DAT_01ad4f3c,0,0,0);
      _DAT_01ad4ed8 = CONCAT44(iVar2,_DAT_01ad4ed8);
      if (-1 < iVar2) {
        iVar2 = thunk_FUN_012ab0d6(iVar2,local_38);
        if (iVar2 == 0) {
          _DAT_01ad4ee8 = CONCAT15(local_2c,0x100000000);
          _DAT_01ad4ee0 = CONCAT44((float)(local_34 & 0xffff),(uint)local_2d);
          _DAT_01ad4ee8 = CONCAT44(_DAT_01ad4eec,(float)(local_34 >> 0x10));
          _DAT_01ad4ef0 = CONCAT11(local_2e == '\x01',DAT_01ad4ef0);
        }
        else {
          thunk_FUN_012aae36(DAT_01ad4edc);
        }
      }
    }
  }
  else {
    _DAT_01ad4f38 = _DAT_01ad4f38 & 0xffffffff;
  }
  _DAT_01ad4ed8 = CONCAT71(DAT_01ad4ed8_1,1);
  if (*plVar1 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

