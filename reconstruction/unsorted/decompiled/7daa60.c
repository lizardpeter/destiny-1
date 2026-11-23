
void FUN_007daa60(void)

{
  long lVar1;
  long lVar2;
  long lVar3;
  long lVar4;
  
  lVar2 = FUN_000af600(0xffff,1,&PTR_DAT_00028008,3,s_GPU_Blitter_Ring_Buffer_0165fd9c,&DAT_026df270
                      );
  lVar3 = 0;
  if (lVar2 != 0) {
    lVar3 = 0;
    do {
      *(undefined4 *)(lVar2 + lVar3) = 0;
      lVar3 = lVar3 + 0x40;
    } while (lVar3 != 0x28000);
    *(undefined8 *)(lVar2 + 0x28000) = 0;
    thunk_FUN_012aa986(lVar2,0,0x28000);
    do {
      lVar1 = *(long *)(lVar2 + 0x28000);
      LOCK();
      lVar4 = *(long *)(lVar2 + 0x28000);
      if (lVar1 == lVar4) {
        *(long *)(lVar2 + 0x28000) = 0;
        lVar4 = lVar1;
      }
      UNLOCK();
      lVar3 = lVar2;
    } while (lVar1 != lVar4);
  }
  DAT_026df268 = lVar3;
  FUN_007db230();
  return;
}

