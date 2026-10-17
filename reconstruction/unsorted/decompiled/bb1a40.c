
void FUN_00bb1a40(undefined4 param_1)

{
  char cVar1;
  undefined8 uVar2;
  int iVar3;
  long local_4188;
  undefined1 local_4180 [20];
  undefined4 local_416c;
  int local_4160;
  int local_4150;
  undefined1 local_40a8 [16512];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  local_416c = 1;
  FUN_00072240(local_4180,local_40a8,0x4080);
  uVar2 = FUN_00346d20();
  FUN_000723b0(local_4180,1);
  FUN_0034b670(uVar2,local_4180,param_1);
  FUN_00072560(local_4180,0);
  cVar1 = FUN_00072210(local_4180);
  if (cVar1 == '\0') {
    iVar3 = (int)(((uint)(local_4160 + 7 + local_4150 >> 0x1f) >> 0x1d) + 7 +
                 local_4160 + local_4150) >> 3;
    local_4188 = 0;
    FUN_00300920(0x4e,iVar3,&local_4188,1);
    if (local_4188 == 0) {
      cVar1 = FUN_005915a0();
      if (cVar1 != '\0') {
        cVar1 = FUN_00591b30();
        if (cVar1 == '\0') {
          FUN_00591b60();
        }
      }
    }
    else {
      thunk_FUN_012aa7c6(*(undefined8 *)(local_4188 + 8),local_40a8,(long)iVar3);
      FUN_00300b90(local_4188);
    }
  }
  if (*DAT_01a1f100 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

