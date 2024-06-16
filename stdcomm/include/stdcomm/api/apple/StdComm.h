//
//  StdCommLog.h
//  api/apple
//
//  Created by ccgo on 2024-06-02.
//  Copyright 2024 ccgo Project Authors. All rights reserved.

#import <Foundation/Foundation.h>

//! \if ZH-CN
//! \file StdCommLog.h
//! \brief stdcomm OC接口文件
//!
//! \author ccgo
//! \else
//! \file StdCommLog.h
//! \brief stdcomm common library OC api file
//!
//! \author ccgo
//! \endif

//! \addtogroup iOS
//! \if ZH-CN
//! StdComm-iOS平台
//! \else
//! StdComm for iOS Platform
//! \endif
//! @{

NS_ASSUME_NONNULL_BEGIN

//! \if ZH-CN
//! \class StdCommLog
//! \brief stdcomm OC接口类
//!
//! \author ccgo
//! \else
//! \class StdCommLog
//! \brief stdcomm common library OC api class
//!
//! \author ccgo
//! \endif
@interface StdComm : NSObject

//-----------------------------------------------------------------------------
//! \if ZH-CN
//!  \name stdcomm-基础
//! \else
//!  \name stdcomm-stdcomm.base
//! \endif
//!  @{
//-----------------------------------------------------------------------------
#pragma mark - stdcomm-base

//! \if ZH-CN
//! \brief 设置调试日志
//!
//! \param isDebugLog 是否启用调试日志
//! \else
//!  \brief set debug log.
//!
//!  \param isDebugLog  the debug log
//! \endif
+ (void)setDebugLog:(BOOL)isDebugLog;

//-----------------------------------------------------------------------------
//!  @}  // end name stdcomm-stdcomm.base
//-----------------------------------------------------------------------------

@end

NS_ASSUME_NONNULL_END

//!  @}  // end group iOS
