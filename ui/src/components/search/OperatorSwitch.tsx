import React, { useEffect, useState } from "react";
import { Switch, Tag, Tooltip, Typography } from "antd";




const OperatorSwitch = ({ isToggleable, mode, setMode }: { isToggleable: boolean, mode: "AND" | "OR", setMode: any }) => {
    const [isAND, setisAND] = useState(mode == "AND" ? true : false)
    useEffect(() => {
        const _isAND = mode == "AND" ? true : false;
        setisAND(_isAND)
    }, [mode])


    return (
        <Tooltip
            title={
                isAND
                    ? "AND logic: Results match ALL selected filters."
                    : "OR logic: Results match ANY selected filter."
            }
        >
            <div className="flex items-center justify-between mb-3 p-2 bg-gray-50 rounded cursor-help">
                <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">Filter Logic:</span>
                    <Tag className="text-gray-500 bg-gray-100 border-gray-300 m-0">
                        {mode}
                    </Tag>
                </div>
                {isToggleable && (
                    <div className="flex items-center gap-2">
                        <Switch
                            checkedChildren={<Typography.Text style={{ fontSize: 10, color: "white" }}>AND</Typography.Text>}
                            unCheckedChildren={<Typography.Text style={{ fontSize: 10, color: "white" }}>OR</Typography.Text>}
                            checked={isAND}
                            onChange={() => isAND ? setMode("OR") : setMode("AND")}
                            size="small"
                        />
                    </div>
                )}
            </div>
        </Tooltip>
    );
}

export default OperatorSwitch;
