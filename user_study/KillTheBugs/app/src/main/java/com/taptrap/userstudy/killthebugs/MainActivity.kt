package com.taptrap.userstudy.killthebugs

import android.animation.AnimatorSet
import android.animation.ObjectAnimator
import android.annotation.SuppressLint
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.ImageView
import androidx.navigation.findNavController
import androidx.navigation.fragment.NavHostFragment

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_game)

        val level = intent.getIntExtra("level", -2)
        val adminMode = intent.getBooleanExtra("adminMode", false)

        if (level > 0) {
            val bundle = Bundle().apply {
                putInt("level", level)
                putBoolean("adminMode", adminMode)
            }
            val navHostFragment = supportFragmentManager
                .findFragmentById(R.id.nav_host_fragment) as? NavHostFragment
            navHostFragment?.navController?.navigate(R.id.action_gameFragment_to_scoreFragment, bundle)
        } else {
            // get circle
            val circle = findViewById<ImageView>(R.id.circle)

            // create animation for circle
            val xAnim = ObjectAnimator.ofFloat(circle, "scaleX", 0.4f, 1f)
            val yAnim = ObjectAnimator.ofFloat(circle, "scaleY", 0.4f, 1f)

            // Combine the animations into a sequence
            val animatorSet = AnimatorSet()
            animatorSet.playSequentially(
                AnimatorSet().apply { // Slam with bounce
                    playTogether(xAnim, yAnim)
                }
            )

            animatorSet.duration = 60000 // Total duration of animation
            animatorSet.start()
        }
    }

    @SuppressLint("MissingSuperCall")
    override fun onBackPressed() {
        // Do nothing to disable the back button
        super.onBackPressed()
    }
}