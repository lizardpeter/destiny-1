
undefined8 FUN_0078ddc0(undefined8 *param_1)

{
  char cVar1;
  undefined8 uVar2;
  long lVar3;
  undefined8 uVar4;
  long local_40;
  long local_38 [3];
  
  local_38[2] = *DAT_01a1f100;
  cVar1 = FUN_005428c0();
  uVar4 = 0;
  if (cVar1 != '\0') {
    uVar2 = FUN_00557c40(&DAT_026bc508);
    local_38[0] = FUN_005863c0(uVar2);
    local_38[1] = 0;
    uVar4 = 1;
    if (local_38[0] != 0) {
      local_40 = FUN_005864b0(uVar2,local_38);
      uVar4 = 2;
      if (local_40 != 0) {
        lVar3 = FUN_00586510(uVar2,local_38);
        uVar4 = 3;
        if ((lVar3 != 0) && (uVar4 = 6, param_1 != (undefined8 *)0x0)) {
          uVar2 = FUN_005845f0(&local_40);
          *param_1 = uVar2;
        }
      }
    }
  }
  if (*DAT_01a1f100 == local_38[2]) {
    return uVar4;
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

