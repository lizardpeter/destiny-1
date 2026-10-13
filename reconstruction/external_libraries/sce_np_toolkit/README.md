# sce_np_toolkit/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `tp.sce_np_toolkit`  
**Folder path evidence:** `HYPOTHESIS` (folder name is a proposal from RTTI/log-channel clustering, not a recovered path)  
**Role:** Sony NP Toolkit, sce::Toolkit::NP (RTTI only)

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

| VA | name | class | evidence | pseudo-C | role |
|---|---|---|---|---|---|
| `0xf90b30` | np_toolkit_thread |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`f90b30_np_toolkit_thread.c`](decompiled/f90b30_np_toolkit_thread.c) | NP toolkit worker thread. |
| `0xfa7e10` | np_toolkit_init |  | CONFIRMED_BINARY (decompiled data flow, runtime traces 2026-10-12/13, backfill); names are HYPOTHESIS | [`fa7e10_np_toolkit_init.c`](decompiled/fa7e10_np_toolkit_init.c) | NP toolkit start-up: sceNpRegisterStateCallback non-zero is failure; its thread (0xF90B30) then tears down and signals the main thread. |

## Classes (94)

Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. Placement in this folder follows the library prefix.

| class | typeinfo | vtable | virtual slots | bases |
|---|---|---|---|---|
| `sce::Json::MemAllocator` | `0x1911c98` |  |  |  |
| `sce::Toolkit::NP::ActivityFeed::Service` | `0x1a13590` | `0x1a13530` | 14 | sce::Toolkit::NP::ServiceImpl |
| `sce::Toolkit::NP::Auth::Service` | `0x1a13620` | `0x1a135c0` | 14 | sce::Toolkit::NP::ServiceImpl |
| `sce::Toolkit::NP::Commerce::Service` | `0x1a13700` | `0x1a136a0` | 14 | sce::Toolkit::NP::ServiceImpl |
| `sce::Toolkit::NP::Controller` | `0x1a11fc0` | `0x1a11f70` | 12 |  |
| `sce::Toolkit::NP::ControllerImpl` | `0x1a12030` | `0x1a11fe0` | 12 | sce::Toolkit::NP::Controller |
| `sce::Toolkit::NP::Friends::Service` | `0x1a122d0` | `0x1a12270` | 14 | sce::Toolkit::NP::ServiceImpl |
| `sce::Toolkit::NP::GameCustomData::Service` | `0x1a121e0` | `0x1a12180` | 14 | sce::Toolkit::NP::ServiceImpl |
| `sce::Toolkit::NP::InGameMessage::Context` | `0x1a124e0` | `0x1a124c0` | 6 | sce::Toolkit::NP::ServiceContext |
| `sce::Toolkit::NP::InGameMessage::Service` | `0x1a12490` | `0x1a12430` | 14 | sce::Toolkit::NP::ServiceImpl |
| `sce::Toolkit::NP::JSONAllocator` | `0x1a137a0` | `0x1a13780` | 6 | sce::Json::MemAllocator |
| `sce::Toolkit::NP::LibraryDatabase` | `0x1a138c0` | `0x1a13810` | 24 | sce::Toolkit::NP::Utilities::Singleton<sce::Toolkit::NP::LibraryDatabase> |
| `sce::Toolkit::NP::LibraryDatabaseImpl` | `0x1a139b0` | `0x1a13900` | 24 | sce::Toolkit::NP::LibraryDatabase |
| `sce::Toolkit::NP::Matching::Context` | `0x1a123b0` | `0x1a12390` | 6 | sce::Toolkit::NP::ServiceContext |
| `sce::Toolkit::NP::Matching::Service` | `0x1a12360` | `0x1a12300` | 14 | sce::Toolkit::NP::ServiceImpl |
| `sce::Toolkit::NP::Messaging::BaseDialog` | `0x1a13ad8` |  |  |  |
| `sce::Toolkit::NP::Messaging::CustomDataDialog` | `0x1a13b10` | `0x1a13ab0` | 7 | sce::Toolkit::NP::Messaging::BaseDialog |
| `sce::Toolkit::NP::Messaging::InvitationDialog` | `0x1a13af0` | `0x1a13a60` | 5 | sce::Toolkit::NP::Messaging::BaseDialog |
| `sce::Toolkit::NP::Messaging::Service` | `0x1a12570` | `0x1a12510` | 14 | sce::Toolkit::NP::ServiceImpl |
| `sce::Toolkit::NP::NetInfo::Service` | `0x1a12600` | `0x1a125a0` | 14 | sce::Toolkit::NP::ServiceImpl |
| `sce::Toolkit::NP::Presence::Service` | `0x1a12730` | `0x1a126d0` | 14 | sce::Toolkit::NP::ServiceImpl |
| `sce::Toolkit::NP::Ranking::Context` | `0x1a128b0` | `0x1a12890` | 6 | sce::Toolkit::NP::ServiceContext |
| `sce::Toolkit::NP::Ranking::Service` | `0x1a12810` | `0x1a127b0` | 14 | sce::Toolkit::NP::ServiceImpl |
| `sce::Toolkit::NP::Service` | `0x1a13a40` | `0x1a139e0` | 14 |  |
| `sce::Toolkit::NP::ServiceContext` | `0x1a137f0` | `0x1a137d0` | 6 |  |
| `sce::Toolkit::NP::ServiceFactory` | `0x1a12078` | `0x1a12060` | 5 |  |
| `sce::Toolkit::NP::ServiceFactoryImpl` | `0x1a120c0` | `0x1a120a0` | 3 | sce::Toolkit::NP::ServiceFactory |
| `sce::Toolkit::NP::ServiceImpl` | `0x1a12150` | `0x1a120f0` | 14 | sce::Toolkit::NP::Service |
| `sce::Toolkit::NP::Sessions::Service` | `0x1a12a80` | `0x1a12a20` | 14 | sce::Toolkit::NP::ServiceImpl |
| `sce::Toolkit::NP::Sns::Service` | `0x1a12b60` | `0x1a12b00` | 14 | sce::Toolkit::NP::ServiceImpl |
| `sce::Toolkit::NP::TSS::Service` | `0x1a12eb0` | `0x1a12e50` | 14 | sce::Toolkit::NP::ServiceImpl |
| `sce::Toolkit::NP::TUS::Service` | `0x1a12fe0` | `0x1a12f80` | 14 | sce::Toolkit::NP::ServiceImpl |
| `sce::Toolkit::NP::Thread` | `0x1a11e28` | `0x1a11df0` | 9 |  |
| `sce::Toolkit::NP::ThreadImpl` | `0x1a11e90` | `0x1a11e50` | 7 | sce::Toolkit::NP::Thread |
| `sce::Toolkit::NP::Trophy::Context` | `0x1a12c40` | `0x1a12c20` | 6 | sce::Toolkit::NP::ServiceContext |
| `sce::Toolkit::NP::Trophy::Service` | `0x1a12bf0` | `0x1a12b90` | 14 | sce::Toolkit::NP::ServiceImpl |
| `sce::Toolkit::NP::UserProfile::Service` | `0x1a13110` | `0x1a130b0` | 14 | sce::Toolkit::NP::ServiceImpl |
| `sce::Toolkit::NP::Utilities::ConditionVariable` | `0x1a14048` |  |  |  |
| `sce::Toolkit::NP::Utilities::ConditionVariableImpl` | `0x1a14030` | `0x1a13fe0` | 9 | sce::Toolkit::NP::Utilities::ConditionVariable |
| `sce::Toolkit::NP::Utilities::Future<int>` | `0x1a11f30` | `0x1a11f20` | 4 | sce::Toolkit::NP::Utilities::FutureImpl |
| `sce::Toolkit::NP::Utilities::Future<sce::Toolkit::NP::NpUser>` | `0x1911d80` | `0x1911d70` | 4 | sce::Toolkit::NP::Utilities::FutureImpl |
| `sce::Toolkit::NP::Utilities::Future<sce::Toolkit::NP::ProductInfoDetailed>` | `0x1911830` | `0x1911820` | 4 | sce::Toolkit::NP::Utilities::FutureImpl |
| `sce::Toolkit::NP::Utilities::Future<std::vector<sce::Toolkit::NP::NpUser, std::allocator<sce::Toolkit::NP::NpUser> > >` | `0x1911b60` | `0x1911b50` | 4 | sce::Toolkit::NP::Utilities::FutureImpl |
| `sce::Toolkit::NP::Utilities::FutureImpl` | `0x1a14080` | `0x1a14070` | 4 |  |
| `sce::Toolkit::NP::Utilities::IJob` | `0x1a121f8` |  |  |  |
| `sce::Toolkit::NP::Utilities::Job<SceNpId>` | `0x1a132a0` | `0x1a13280` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<SceNpOnlineId>` | `0x1a132f0` | `0x1a132d0` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<SceNpTrophyGameData>` | `0x1a12d80` | `0x1a12d60` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<SceNpTssDataStatus>` | `0x1a12f00` | `0x1a12ee0` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<int>` | `0x1a12400` | `0x1a123e0` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::CountryInfo>` | `0x1a13200` | `0x1a131e0` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::FriendsRankInformation>` | `0x1a12900` | `0x1a128e0` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::MessageAttachment>` | `0x1a12240` | `0x1a12220` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::NetStateBasic>` | `0x1a126a0` | `0x1a12680` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::NetStateDetailed>` | `0x1a12650` | `0x1a12630` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::NpSessionInformation>` | `0x1a12ad0` | `0x1a12ab0` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::NpUser>` | `0x1a131b0` | `0x1a13190` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::NpUsers>` | `0x1a13160` | `0x1a13140` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::PresenceInfo>` | `0x1a12780` | `0x1a12760` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::ProductInfoDetailed>` | `0x1a13750` | `0x1a13730` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::RankInformation>` | `0x1a12950` | `0x1a12930` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::Ranking::CacheArgs>` | `0x1a12860` | `0x1a12840` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::RegisterTrophyRequest>` | `0x1a12e20` | `0x1a12e00` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::TempRank>` | `0x1a129f0` | `0x1a129d0` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::Ticket>` | `0x1a13670` | `0x1a13650` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::TrophyGameInfo>` | `0x1a12d30` | `0x1a12d10` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::TrophyGroupInfo>` | `0x1a12c90` | `0x1a12c70` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::TrophyInfo>` | `0x1a12ce0` | `0x1a12cc0` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::TssData>` | `0x1a12f50` | `0x1a12f30` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::TusDataOutput>` | `0x1a13030` | `0x1a13010` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::UnlockTrophyRequest>` | `0x1a12dd0` | `0x1a12db0` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::UserRankInformation>` | `0x1a129a0` | `0x1a12980` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<sce::Toolkit::NP::WordFilterSanitized>` | `0x1a13500` | `0x1a134e0` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<std::basic_string<char, std::char_traits<char>, std::allocator<char> > >` | `0x1a13250` | `0x1a13230` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Job<std::vector<SceNpTusVariable, std::allocator<SceNpTusVariable> > >` | `0x1a13080` | `0x1a13060` | 3 | sce::Toolkit::NP::Utilities::IJob |
| `sce::Toolkit::NP::Utilities::Mutex` | `0x1a140f8` |  |  |  |
| `sce::Toolkit::NP::Utilities::MutexImpl` | `0x1a140e0` | `0x1a140a0` | 7 | sce::Toolkit::NP::Utilities::Mutex |
| `sce::Toolkit::NP::Utilities::Singleton<sce::Toolkit::NP::LibraryDatabase>` | `0x1a138d8` |  |  |  |
| `sce::Toolkit::NP::Utilities::SyncFlag` | `0x1a11ee0` |  |  |  |
| `sce::Toolkit::NP::Utilities::SyncFlagImpl` | `0x1a11ef0` | `0x1a11ec0` | 8 | sce::Toolkit::NP::Utilities::SyncFlag |
| `sce::Toolkit::NP::WebAPI::ActivityFeedGroup` | `0x1a13fb0` | `0x1a13f70` | 7 | sce::Toolkit::NP::WebAPI::BaseGroup |
| `sce::Toolkit::NP::WebAPI::BaseGroup` | `0x1a13bc8` | `0x1a13b40` | 7 |  |
| `sce::Toolkit::NP::WebAPI::BlockListGroup` | `0x1a13e10` | `0x1a13db0` | 10 | sce::Toolkit::NP::WebAPI::FriendGroup |
| `sce::Toolkit::NP::WebAPI::CommerceGroup` | `0x1a13c50` | `0x1a13c10` | 7 | sce::Toolkit::NP::WebAPI::BaseGroup |
| `sce::Toolkit::NP::WebAPI::Context` | `0x1a133d0` | `0x1a133b0` | 6 | sce::Toolkit::NP::ServiceContext |
| `sce::Toolkit::NP::WebAPI::CustomDataGroup` | `0x1a13cc0` | `0x1a13c80` | 7 | sce::Toolkit::NP::WebAPI::BaseGroup |
| `sce::Toolkit::NP::WebAPI::EntitlementsGroup` | `0x1a13d30` | `0x1a13cf0` | 7 | sce::Toolkit::NP::WebAPI::BaseGroup |
| `sce::Toolkit::NP::WebAPI::FriendGroup` | `0x1a13df0` | `0x1a13d60` | 8 | sce::Toolkit::NP::WebAPI::BaseGroup |
| `sce::Toolkit::NP::WebAPI::PresenceGroup` | `0x1a13be0` | `0x1a13b90` | 9 | sce::Toolkit::NP::WebAPI::BaseGroup |
| `sce::Toolkit::NP::WebAPI::Service` | `0x1a13380` | `0x1a13320` | 14 | sce::Toolkit::NP::ServiceImpl |
| `sce::Toolkit::NP::WebAPI::SessionGroup` | `0x1a13e80` | `0x1a13e40` | 7 | sce::Toolkit::NP::WebAPI::BaseGroup |
| `sce::Toolkit::NP::WebAPI::UserProfileGroup` | `0x1a13f00` | `0x1a13eb0` | 9 | sce::Toolkit::NP::WebAPI::BaseGroup |
| `sce::Toolkit::NP::WordFilter::Context` | `0x1a134b0` | `0x1a13490` | 6 | sce::Toolkit::NP::ServiceContext |
| `sce::Toolkit::NP::WordFilter::Service` | `0x1a13460` | `0x1a13400` | 14 | sce::Toolkit::NP::ServiceImpl |

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
