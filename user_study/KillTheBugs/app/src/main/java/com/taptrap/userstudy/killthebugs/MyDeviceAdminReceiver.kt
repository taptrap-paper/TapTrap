package com.taptrap.userstudy.killthebugs

import android.app.admin.DeviceAdminReceiver
import android.content.Context
import android.content.Intent
import android.util.Log

class MyDeviceAdminReceiver : DeviceAdminReceiver() {

    override fun onEnabled(context: Context, intent: Intent) {
        super.onEnabled(context, intent)

        Log.d("ADMIN", "onEnabled")

        val levelActivity = Intent(context, LevelActivity::class.java)
        levelActivity.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        levelActivity.putExtra("points", 1)
        levelActivity.putExtra("level", 4)
        context.startActivity(levelActivity)
    }

    override fun onDisabled(context: Context, intent: Intent) {
        Log.d("ADMIN", "onDisabled")
        super.onDisabled(context, intent)
    }
}