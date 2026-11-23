
void FUN_00577410(long param_1)

{
  char cVar1;
  undefined4 uVar2;
  long lVar3;
  undefined8 uVar4;
  undefined8 *puVar5;
  long *plVar6;
  long lVar7;
  undefined **local_48;
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar3 = FUN_0057d940();
  FUN_005781b0(param_1);
  plVar6 = (long *)(param_1 + 0x2dc8);
  lVar7 = 0x10;
  do {
    if ((*(long *)(lVar3 + lVar7) == 0) || (uVar4 = FUN_0056b260(), *(long *)(lVar3 + lVar7) == 0))
    {
LAB_005774a0:
      cVar1 = (**(code **)(*plVar6 + 0x70))(plVar6);
      if (cVar1 != '\0') {
        FUN_00578100();
      }
    }
    else {
      uVar2 = FUN_00001df0(uVar4);
      puVar5 = (undefined8 *)FUN_0056dc00(uVar4,0,uVar2,lVar3 + lVar7);
      if (puVar5 == (undefined8 *)0x0) goto LAB_005774a0;
      local_40 = *puVar5;
      local_48 = &PTR_FUN_0193ebc0;
      FUN_00577c60(param_1,&local_40,puVar5 + 1,plVar6,&local_48,0);
    }
    plVar6 = plVar6 + 0x2d;
    lVar7 = lVar7 + 0x10;
    if (lVar7 == 0x150) {
      if (*DAT_01a1f100 != local_38) {
        thunk_FUN_012aa7f6();
        return;
      }
      return;
    }
  } while( true );
}

