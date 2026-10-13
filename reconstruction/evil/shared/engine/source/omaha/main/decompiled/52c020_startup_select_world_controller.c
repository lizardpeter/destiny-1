
void FUN_0052c020(void)

{
  long *plVar1;
  char cVar2;
  char cVar3;
  int iVar4;
  undefined1 local_28 [8];
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  (**(code **)PTR_PTR_01938638)(&PTR_PTR_01938638);
  FUN_00bddd30();
  FUN_00b9b720();
  FUN_00be9d70();
  FUN_00bef520();
  FUN_00bf5670();
  FUN_00c29150();
  (**(code **)(PTR_PTR_01938638 + 8))(&PTR_PTR_01938638);
  thunk_FUN_0052a730();
  FUN_00324260();
  FUN_005e3d90();
  FUN_001d6ec0();
  FUN_00346de0();
  FUN_003d9b70();
  FUN_005a4400();
  FUN_005426e0();
  FUN_002b37c0();
  FUN_0058bf90();
  FUN_00744640();
  FUN_00500760();
  FUN_0050fd00();
  FUN_0058bf90();
  FUN_00116ad0();
  FUN_007cd4a0();
  FUN_00648f30();
  FUN_0052af30();
  FUN_00743500();
  FUN_006b59b0();
  FUN_00674410();
  FUN_00715cf0();
  FUN_005c45a0();
  FUN_007506d0();
  cVar2 = FUN_00239b50();
  cVar3 = '\x02';
  if (cVar2 == '\0') {
    cVar3 = FUN_00239bc0();
  }
  FUN_00135090(local_28,cVar3,3,6);
  FUN_0042e2e0(cVar3 == '\x02');
  FUN_0041d110(cVar3 == '\x02');
  FUN_004cc970();
  FUN_0031f4e0();
  FUN_00491a10();
  FUN_002fc010();
  FUN_004e27e0();
  FUN_004e2520();
  FUN_005a88e0();
  FUN_00515f50();
  FUN_0073d060();
  FUN_0052f710();
  FUN_00510e40();
  FUN_0092d260();
  FUN_00241c00(FUN_0052cb30);
  iVar4 = FUN_0001cf60();
  if (iVar4 == -1) {
    cVar2 = FUN_00239b70();
    iVar4 = 2;
    if (cVar2 == '\0') {
      iVar4 = FUN_000c5b70();
      iVar4 = (uint)(iVar4 != 2) + (uint)(iVar4 != 2) * 2;
    }
  }
  FUN_00751ee0(iVar4);
  FUN_001cf9a0();
  FUN_00326630();
  FUN_0032cfa0();
  if (*plVar1 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

