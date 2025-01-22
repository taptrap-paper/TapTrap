package com.taptrap.userstudy.killthebugs

import android.content.Context
import android.graphics.Color
import android.net.Uri
import androidx.browser.customtabs.CustomTabsCallback
import androidx.browser.customtabs.CustomTabsClient
import androidx.browser.customtabs.CustomTabsIntent
import androidx.browser.customtabs.CustomTabsServiceConnection
import androidx.browser.customtabs.CustomTabsSession
import android.util.Log

class CustomTabHelper(private val context: Context, private val clickListener: ClickListener?) {

    private var customTabsClient: CustomTabsClient? = null
    private var customTabsSession: CustomTabsSession? = null
    private var startedCount = 0
    private lateinit var rawURL: String

    // Service connection for Custom Tabs
    private val customTabsServiceConnection = object : CustomTabsServiceConnection() {
        override fun onCustomTabsServiceConnected(name: android.content.ComponentName, client: CustomTabsClient) {
            customTabsClient = client
            customTabsClient?.warmup(0L) // Preload resources
            customTabsSession = customTabsClient?.newSession(customTabsCallback)
            customTabsSession?.mayLaunchUrl(Uri.parse(rawURL), null, null)
        }

        override fun onServiceDisconnected(name: android.content.ComponentName) {
            customTabsClient = null
            customTabsSession = null
        }
    }

    init {
        rawURL = context.getString(R.string.webapp)
        // Bind to Custom Tabs service
        CustomTabsClient.bindCustomTabsService(context, "com.android.chrome", customTabsServiceConnection)
    }

    // Callback to monitor URL changes
    private val customTabsCallback = object : CustomTabsCallback() {
        override fun onNavigationEvent(navigationEvent: Int, extras: android.os.Bundle?) {
            when (navigationEvent) {
                NAVIGATION_STARTED -> {
                    Log.d("CustomTabs", "Navigation started")
                    startedCount++
                    if (startedCount == 2) {
                        clickListener?.clicked(true)
                        //(context as MainActivity).clicked()
                    }
                }
                NAVIGATION_FINISHED -> Log.d("CustomTabs", "Navigation finished")
                NAVIGATION_FAILED -> Log.d("CustomTabs", "Navigation failed")
            }
        }
    }

    fun openCustomTabHowTo(url: String) {
        val customTabsIntent = CustomTabsIntent.Builder(customTabsSession)
            .setShowTitle(true)
            .setToolbarColor(Color.parseColor("#6200EA"))
            .setStartAnimations(context, 0, 0)
            .setExitAnimations(context, 0, 0)
            .setShareState(CustomTabsIntent.SHARE_STATE_OFF)
            .setUrlBarHidingEnabled(false)
            .build()

        // Launch URL in Custom Tab
        customTabsIntent.launchUrl(context, Uri.parse(url))
    }

    // Launch a Custom Tab with the specified URL
    fun openCustomTab(url: String, adminMode: Boolean) {

        val fadeIn: Int
        if (adminMode) {
            fadeIn = R.anim.fade_in_ct_admin
        } else {
            fadeIn = R.anim.fade_in_ct
        }

        val customTabsIntent = CustomTabsIntent.Builder(customTabsSession)
            .setStartAnimations(context, fadeIn, R.anim.fade_out)
            .setShowTitle(true)
            .build()

        // Launch URL in Custom Tab
        customTabsIntent.launchUrl(context, Uri.parse(url))
    }

    fun unbindService() {
        context.unbindService(customTabsServiceConnection)
    }
}
