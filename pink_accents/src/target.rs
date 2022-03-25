use std::collections::HashMap;
use std::fmt::Debug;
use std::ops::Range;

use rand::prelude::*;

use rand_distr::WeightedAliasIndex;

use crate::capture::Capture;

pub trait Target: Debug + Send + Sync {
    fn init(&mut self, _severity_range: Range<i32>) {}

    fn callback(&self, caps: Capture) -> &str;
}

#[derive(Debug)]
pub struct DirectTarget {
    pub replacement: &'static str,
}

impl Target for DirectTarget {
    fn callback(&self, _: Capture) -> &str {
        self.replacement
    }
}

impl Target for &str {
    fn callback(&self, _: Capture) -> &str {
        self
    }
}

#[derive(Debug)]
pub struct MultiTarget {
    pub replacement: Vec<Box<dyn Target>>,
}

impl Target for MultiTarget {
    fn callback(&self, caps: Capture) -> &str {
        let selected = self.replacement.choose(&mut rand::thread_rng()).unwrap();

        selected.callback(caps)
    }
}

type WeightComputerCallable = Box<dyn Fn(i32) -> f32>;

enum WeightComputer {
    Stable(WeightComputerCallable),
    Unstable(WeightComputerCallable),
}

#[derive(Debug)]
pub struct MapTarget {
    targets: Vec<Option<Box<dyn Target>>>,
    weighted_dist: WeightedAliasIndex<f32>,
}

impl MapTarget {
    fn new(replacement: HashMap<Box<dyn Target>, f32>) -> Self {
        let mut targets = Vec::with_capacity(replacement.len());
        let mut weights = Vec::with_capacity(replacement.len());

        for (target, weight) in replacement.into_iter() {
            targets.push(Some(target));
            weights.push(weight);
        }

        Self {
            targets,
            weighted_dist: WeightedAliasIndex::new(weights).unwrap(),
        }
    }
}

impl Target for MapTarget {
    fn init(&mut self, severity_range: Range<i32>) {}

    fn callback(&self, caps: Capture) -> &str {
        if let Some(selected) = &self.targets[self.weighted_dist.sample(&mut rand::thread_rng())] {
            selected.callback(caps)
        } else {
            panic!("no");
            // caps.original()
        }
    }
}
